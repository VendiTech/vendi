import json
import os

from mspy_vendi.core.schemas.nayax import NayaxTransactionSchema


def test_nayax_schema():
    path_to_examples: str = os.getenv("PREFIX_APP", "") + "/tests/mocking/nayax/nayax-data.json"

    with open(path_to_examples, "r") as file:
        list_of_examples: list[dict] = json.loads(file.read())

    for nayax_example in list_of_examples:
        result = NayaxTransactionSchema.model_validate(nayax_example)

        assert result.transaction_id == nayax_example["TransactionId"]
        assert result.machine_id == nayax_example["MachineId"]

        assert result.data.machine_id == nayax_example["Data"]["Machine ID"]
        assert result.data.area_description == nayax_example["Data"]["Area Description"]
        assert result.data.actor_description == nayax_example["Data"]["Actor Description"]
        assert result.data.actor_id == nayax_example["Data"]["Actor ID"]
        assert result.data.area_description == nayax_example["Data"]["Area Description"]

        for pydantic_record, initial_record in zip(
            sorted(result.data.products, key=lambda item: item.product_id),
            sorted(nayax_example["Data"]["Products"], key=lambda item: item["Product ID"]),
        ):
            assert pydantic_record.product_id == initial_record["Product ID"]
            assert pydantic_record.product_name == initial_record["Product Name"]
            assert pydantic_record.product_group == initial_record["Product Group"]
            assert (
                pydantic_record.product_quantity == initial_record["Product Quantity"]
                and pydantic_record.product_quantity >= 0
            )
            assert pydantic_record.product_bruto == initial_record["Product Bruto"]
