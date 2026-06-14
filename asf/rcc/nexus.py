from __future__ import annotations

from asf.core.artifact import ASFArtifact
from asf.rcc.route import RCCRoute, build_route


def orient(artifact: ASFArtifact, action: str) -> RCCRoute:
    return build_route(artifact.artifact_id, action)

