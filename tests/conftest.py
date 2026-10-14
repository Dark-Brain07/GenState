"""
Shared direct-mode test configuration and Windows compatibility patch for GenState.
"""

import os
import sys
import tempfile
import pytest

try:
    import gltest.direct.loader as loader

    def patched_inject_message_to_fd0(vm):
        try:
            from genlayer.py import calldata
            from genlayer.py.types import Address
        except ImportError:
            return

        sender_addr = vm.sender
        if isinstance(sender_addr, bytes):
            sender_addr = Address(sender_addr)

        contract_addr = vm._contract_address
        if isinstance(contract_addr, bytes):
            contract_addr = Address(contract_addr)

        origin_addr = vm.origin
        if isinstance(origin_addr, bytes):
            origin_addr = Address(origin_addr)

        message_data = {
            'contract_address': contract_addr,
            'sender_address': sender_addr,
            'origin_address': origin_addr,
            'stack': [],
            'value': vm._value,
            'datetime': vm._datetime,
            'is_init': False,
            'chain_id': vm._chain_id,
            'entry_kind': 0,
            'entry_data': b'',
            'entry_stage_data': None,
        }

        encoded = calldata.encode(message_data)

        fd, path = tempfile.mkstemp()
        try:
            os.write(fd, encoded)
            os.lseek(fd, 0, os.SEEK_SET)

            original_stdin = os.dup(0)
            vm._original_stdin_fd = original_stdin

            os.dup2(fd, 0)
        finally:
            os.close(fd)
            try:
                os.unlink(path)
            except Exception:
                # On Windows, fd 0 holds an open handle preventing unlink until closed
                pass

    loader._inject_message_to_fd0 = patched_inject_message_to_fd0
except Exception:
    pass


@pytest.fixture(autouse=True)
def _patch_direct_vm_datetime(direct_vm):
    """Ensure direct_vm.warp correctly updates gl.message_raw['datetime']."""
    original_refresh = direct_vm._refresh_gl_message

    def refresh_with_datetime():
        original_refresh()
        gl = sys.modules.get("genlayer.gl")
        if gl is not None and isinstance(getattr(gl, "message_raw", None), dict):
            gl.message_raw["datetime"] = direct_vm._datetime

    direct_vm._refresh_gl_message = refresh_with_datetime
    direct_vm._refresh_gl_message()
    yield


@pytest.fixture(autouse=True)
def _reset_contract_registry():
    """Allow every direct test to deploy the contract independently."""
    yield
    try:
        import genlayer.gl.genvm_contracts as contracts
    except ImportError:
        return
    contracts.__known_contract__ = None
