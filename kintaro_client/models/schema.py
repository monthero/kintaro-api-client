from collections import OrderedDict
from re import Match, Pattern, compile as re_compile
from typing import Dict, List, Optional

from .base import BaseKintaroEntity


CHARACTER_LIMITS_PATTERN: Pattern = re_compile(r"^\^\.{(\d*,\d*)}\$$")


class KintaroSchemaField(BaseKintaroEntity):
    name: Optional[str] = None
    description: Optional[str] = None
    type: Optional[str] = None
    required: bool = False
    repeated: bool = False
    translatable: bool = False
    locale_varied: bool = False
    validation_rule: Optional[str] = None
    validation_rule_message: Optional[str] = None
    schema_fields: List[Dict] = []

    def __init__(self, initial_data: Optional[Dict] = None):
        if not initial_data:
            return

        processed_data: Dict = {}
        for key, value in initial_data.items():
            if key.startswith("can_") or key in [
                "displayed",
                "path_info",
                "locale_varied_translatable",
                "label",
                "restriction",
                "fallback_strategy",
                "repo_id",
                "indexed",
            ]:
                continue
            elif key == "schema_fields":
                setattr(
                    self,
                    "schema_fields",
                    [
                        KintaroSchemaField(initial_data=field)
                        for field in initial_data.get("schema_fields", [])
                    ],
                )

            if (
                key in ["validation_rule", "validation_rule_message"]
                and value == ""
            ):
                value = None

            processed_data[key] = value

        super().__init__(initial_data=processed_data)

    def __repr__(self) -> str:
        return f"KintaroSchemaField<{self.name}>"

    def to_json(self) -> Dict:
        obj: Dict = super().to_json()
        ordered_keys: List[str] = [
            "name",
            "type",
            "required",
            "repeated",
            "translatable",
            "locale_varied",
            "description",
            "default",
            "choices",
            "schema_name",
            "schema_fields",
        ]
        return OrderedDict(
            (key, obj.get(key))
            for key in sorted(obj.keys(), key=lambda k: ordered_keys.index(k))
        )


class KintaroSchema(BaseKintaroEntity):
    name: Optional[str] = None
    repo_id: Optional[str] = None
    schema_fields: List[KintaroSchemaField] = []
    character_limits: Optional[Dict] = None

    def __init__(self, initial_data: Optional[Dict] = None):
        if not initial_data:
            return

        super().__init__(initial_data=initial_data)

        for key in initial_data:
            if key == "schema_fields":
                setattr(
                    self,
                    "schema_fields",
                    [
                        KintaroSchemaField(initial_data=field)
                        for field in initial_data.get("schema_fields", [])
                    ],
                )

        self.add_field_character_limits_obj(
            schema_name=self.name,
            schema_fields=self.schema_fields or [],
        )

    def __repr__(self) -> str:
        return f"KintaroSchema<{self.name}>"

    def add_field_character_limits_obj(
        self, schema_name: str, schema_fields: List[KintaroSchemaField]
    ):
        field: KintaroSchemaField
        for field in schema_fields:
            if getattr(field, "validation_rule", None):
                match: Optional[Match] = CHARACTER_LIMITS_PATTERN.search(
                    field.validation_rule
                )
                if match:
                    min_chars: Optional[int]
                    max_chars: Optional[int]
                    min_chars, max_chars = [
                        int(part) if part else None
                        for part in match.group(1).split(",")
                    ]

                    if (
                        min_chars is not None
                        and max_chars is not None
                        and max_chars <= min_chars
                    ):
                        raise ValueError(
                            f"Character limitations expression for field "
                            f"{field.name} within schema {schema_name} "
                            f"are incorrectly specified -> "
                            f"{field.validation_rule}"
                        )

                    setattr(
                        field,
                        "character_limits",
                        dict(
                            min=min_chars,
                            max=max_chars,
                        ),
                    )

                    field_name: str = field.name.title()

                    message: str = (
                        f"{field_name} should have between "
                        f"{min_chars}"
                        f" and {max_chars} characters"
                    )
                    if min_chars is None and max_chars is None:
                        message = ""
                    elif min_chars is None and max_chars is not None:
                        message = (
                            f"{field_name} should have less than "
                            f"{max_chars} characters"
                        )
                    elif min_chars is not None and max_chars is None:
                        message = (
                            f"{field_name} should have more than "
                            f"{min_chars} characters"
                        )

                    setattr(field, "validation_rule_message", message)

            if getattr(field, "schema_fields", []):
                self.add_field_character_limits_obj(
                    schema_name=(
                        f"{schema_name} ->"
                        f"' {getattr(field, 'schema_name', field.type)}'"
                    ),
                    schema_fields=getattr(field, "schema_fields", []),
                )

    def to_json(self):
        original_obj = super().to_json()
        obj = OrderedDict(
            [
                ("name", original_obj.get("name")),
                ("collection_id", original_obj.get("collection_id")),
                ("schema_fields", original_obj.get("schema_fields")),
            ]
        )

        ordered_keys = [
            "name",
            "type",
            "required",
            "repeated",
            "translatable",
            "locale_varied",
            "validate",
            "validation_rule",
            "validation_rule_message",
            "character_limits",
            "description",
            "default",
            "choices",
            "collections",
            "schema_name",
            "schema_fields",
        ]

        for sf_idx, sf in enumerate(original_obj.get("schema_fields", [])):
            obj["schema_fields"][sf_idx] = OrderedDict(
                (key, sf.get(key))
                for key in sorted(
                    sf.keys(), key=lambda k: ordered_keys.index(k)
                )
            )
        return obj
