import json
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional

from models.blueprint import Blueprint, BlueprintCreateInput

# Fixed namespace for all Evercrafted deterministic IDs.
# Never change this value — doing so invalidates all existing stored IDs.
_EC_NAMESPACE = uuid.UUID("ec000000-0000-0000-0000-000000000001")

_store: Dict[str, Blueprint] = {}


def _deterministic_id(input_data: BlueprintCreateInput) -> str:
    seed = json.dumps(
        {
            "name": input_data.name,
            "tone": input_data.emotion.tone.value,
            "intensity": input_data.emotion.intensity,
        },
        sort_keys=True,
    )
    return str(uuid.uuid5(_EC_NAMESPACE, seed))


def create_blueprint(input_data: BlueprintCreateInput) -> Blueprint:
    now = datetime.now(timezone.utc).isoformat()
    blueprint = Blueprint(
        id=_deterministic_id(input_data),
        schema_version=input_data.schema_version,
        name=input_data.name,
        status=input_data.status,
        emotion=input_data.emotion,
        created_at=now,
        updated_at=now,
    )
    _store[blueprint.id] = blueprint
    return blueprint


def get_blueprint(blueprint_id: str) -> Optional[Blueprint]:
    return _store.get(blueprint_id)


def list_blueprints() -> List[Blueprint]:
    return list(_store.values())
