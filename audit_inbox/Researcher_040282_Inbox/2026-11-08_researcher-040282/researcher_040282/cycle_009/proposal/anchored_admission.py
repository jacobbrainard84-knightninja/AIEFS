"""New-file caller-anchored admission proposal, not an installed authority.
The caller must trust the anchor independently of the supplied input directory.
Static-input byte admission only: no physics proof or atomic/TOCTOU guarantee.
"""
import hashlib
from pathlib import Path
import re


class TrustConfigurationError(ValueError):
    """Missing/malformed caller policy is a configuration blocker, not a negative."""


class ManifestTrustError(ValueError):
    def __init__(self, code='manifest_not_anchored'):
        self.code=code
        super().__init__(code)


def require_manifest_anchor(path, expected_manifest_sha256):
    if not isinstance(expected_manifest_sha256,str) or re.fullmatch('[0-9a-f]{64}',expected_manifest_sha256) is None:
        raise TrustConfigurationError('An independently selected lowercase SHA256 anchor is required')
    digest=hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda:stream.read(1024*1024),b''):
            digest.update(block)
    observed=digest.hexdigest()
    if observed!=expected_manifest_sha256:
        raise ManifestTrustError()
    return observed


def validate_anchored(inputs, *, expected_manifest_sha256, validate_run):
    """Require the external root BEFORE delegating to unchanged validate_run.
    Return its exact object; its child-hash/schema checks are never replaced.
    The post-check is only a persistent-manifest-change tripwire, not atomic I/O.
    """
    require_manifest_anchor(inputs.manifest,expected_manifest_sha256)
    result=validate_run(inputs)
    try:
        require_manifest_anchor(inputs.manifest,expected_manifest_sha256)
    except ManifestTrustError as error:
        raise ManifestTrustError('manifest_changed_during_validation') from error
    return result
