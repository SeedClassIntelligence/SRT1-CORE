from setuptools import setup
from setuptools.command.build_py import build_py as _build_py


EXCLUDED_PUBLIC_CORE_MODULES = {
    "srt1_platform.audit_ledger",
    "srt1_platform.consistency_auditor",
    "srt1_platform.delta_auditor",
    "srt1_platform.governance_monitor",
    "srt1_platform.proxy_engine",
    "srt1_platform.remote_auth",
    "srt1_platform.srt1_sion_cli",
    "srt1_pro.execution_engine",
    "srt1_pro.self_heal",
}


class build_py(_build_py):
    """Exclude private/future modules from public Core wheels."""

    def find_package_modules(self, package, package_dir):
        modules = super().find_package_modules(package, package_dir)
        return [
            (pkg, mod, file_path)
            for pkg, mod, file_path in modules
            if f"{pkg}.{mod}" not in EXCLUDED_PUBLIC_CORE_MODULES
        ]


setup(cmdclass={"build_py": build_py})
