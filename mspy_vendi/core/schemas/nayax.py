from datetime import datetime
from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, NonNegativeInt

from mspy_vendi.core.helpers import to_title_case

OptionalFloat = Annotated[float | None, Field(None)]
OptionalString = Annotated[str | None, Field(None)]
OptionalInt = Annotated[int | None, Field(None)]
OptionalDatetime = Annotated[datetime | None, Field(None)]
OptionalBool = Annotated[bool | None, Field(None)]
OptionalUUID = Annotated[UUID | None, Field(None)]


class NayaxBaseModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_title_case, populate_by_name=True, validate_assignment=True)


class NayaxProductSchema(NayaxBaseModel):
    product_name_mdb_code_pa_code_price: OptionalString = Field(
        None, alias="Product(Product Name(MDB Code,PA Code=Price))"
    )
    product_group: OptionalString
    product_code_in_map: OptionalInt = Field(None, alias="Product Code in Map")
    product_pa_code: OptionalString = Field(None, alias="Product PA Code")
    product_volume_type: OptionalString
    product_name: OptionalString
    product_vat_id: OptionalString = Field(None, alias="Product VAT Id")
    product_tax_value: OptionalString
    product_tax_code: OptionalString
    product_vat_amount: OptionalInt
    product_net_price: OptionalInt
    product_external_prepaid_price: OptionalInt
    product_group_code: OptionalInt  # Change from String
    product_group_sub_code: OptionalInt  # Change from String
    product_retail_price: OptionalFloat  # Change from String
    product_discount_percentage: OptionalFloat
    product_discount_amount: OptionalFloat
    product_bruto: OptionalFloat
    product_catalog_number: OptionalString
    product_unit_of_measure: OptionalInt
    product_quantity: NonNegativeInt | None = None
    product_id: OptionalInt = Field(None, alias="Product ID")


class NayaxDataSchema(NayaxBaseModel):
    machine_name: OptionalString
    operator_identifier: OptionalString
    machine_au_time: OptionalDatetime = Field(None, alias="Machine AuTime")
    machine_se_time: OptionalDatetime = Field(None, alias="Machine SeTime")
    currency: OptionalString
    card_string: OptionalString
    brand: OptionalString
    cli: OptionalString = Field(None, alias="CLI")
    se_value: OptionalFloat = Field(None, alias="SeValue")
    extra_charge: OptionalFloat
    payment_service: OptionalString = Field(None, alias="Payment Service(Mobile using Credit Card)")
    payment_method_id: OptionalInt = Field(None, alias="Payment Method ID (1)")
    recognition_method_id: OptionalInt = Field(None, alias="Recognition Method ID (3)")
    catalog_number: OptionalString
    device_number: OptionalString
    actor_hierarchy: OptionalString
    payment_method_description: OptionalString
    recognition_description: OptionalString
    card_first_4_digits: OptionalString
    card_last_4_digits: OptionalString
    card_type: OptionalString
    machine_group: OptionalString
    transaction_id: OptionalInt = Field(None, alias="Transaction ID")
    site_id: OptionalInt = Field(None, alias="Site ID")
    authorization_time: OptionalDatetime = Field(None, alias="Authorization Time")
    authorization_value: OptionalFloat = Field(None, alias="Authorization Value")
    pay_serv_trans_id: OptionalString = Field(None, alias="PayServTransid")
    se_pay_serv_trans_id: OptionalString = Field(None, alias="sePayServTransId")
    settlement_time: OptionalDatetime = Field(None, alias="Settlement Time")
    cancel_type: OptionalString
    is_revalue_transaction: OptionalBool
    preselection_status: OptionalInt
    is_phone_registration: OptionalBool
    is_multivend: OptionalBool
    settlment_failed: OptionalBool
    sale_id: OptionalInt = Field(None, alias="Sale ID")
    sale_value: OptionalFloat
    updated_dt: OptionalDatetime = Field(None, alias="Updated DT")
    constant_preauthorization_value: OptionalString
    is_partial_confirmation: OptionalBool
    authorization_code: OptionalString
    authorization_date_and_time: OptionalDatetime = Field(None, alias="Authorization Date and Time")
    authorization_rrn: OptionalString = Field(None, alias="Authorization RRN")
    event_code: OptionalInt
    guest_name: OptionalString
    token: OptionalString
    zip_code: OptionalString
    billing_provider_id: OptionalInt = Field(None, alias="Billing Provider ID")
    avs_only: OptionalBool = Field(None, alias="AVS Only")
    bod_transaction_key: OptionalString = Field(None, alias="BOD Transaction Key")
    disable_debit_cards: OptionalString
    force_transactions_terminal: OptionalString
    use_phone_transaction: OptionalBool
    license_id: OptionalInt = Field(None, alias="License ID")
    merchant_id: OptionalString = Field(None, alias="Merchant ID")
    billing_site_id: OptionalInt = Field(None, alias="Billing Site ID")
    terminal_id: OptionalInt = Field(None, alias="Terminal ID")
    user_password: OptionalString
    with_zip: OptionalBool = Field(None, alias="With ZIP")
    use_phone_contactless: OptionalBool
    use_phone_contact: OptionalBool
    debit_card_prefix: OptionalString
    actor_description: OptionalString
    institute_description: OptionalString
    location_code: OptionalString
    location_description: OptionalString
    operator_institute_code: OptionalString
    area_description: OptionalString
    op_button_code: OptionalString = Field(None, alias="OP Button Code")
    barcode: OptionalString
    cost_price: OptionalFloat
    card_price: OptionalFloat
    prepaid_price: OptionalFloat
    machine_price: OptionalFloat
    cash_price: OptionalFloat
    default_price: OptionalFloat
    actor_code: OptionalInt
    display_card_number: OptionalString  # Maybe bool
    card_holder_name: OptionalString
    user_identity: OptionalString
    billing_provider_name: OptionalString
    is_offline_transaction: OptionalBool
    is_emv_transaction: OptionalBool = Field(None, alias="Is EMV Transaction")
    machine_autime_date_only: OptionalString = Field(None, alias="Machine AuTime (Date only)")
    machine_autime_time_only: OptionalString = Field(None, alias="Machine AuTime (Time only)")
    machine_setime_date_only: OptionalString = Field(None, alias="Machine SeTime (Date only)")
    machine_setime_time_only: OptionalString = Field(None, alias="Machine SeTime (Time only)")
    settlement_time_date_only: OptionalString = Field(None, alias="Settlement Time (Date only)")
    settlement_time_time_only: OptionalString = Field(None, alias="Settlement Time (Time only)")
    updated_dt_date_only: OptionalString = Field(None, alias="Updated DT (Date only)")
    updated_dt_time_only: OptionalString = Field(None, alias="Updated DT (Time only)")
    raw_eni_loyalty_num: OptionalString = Field(None, alias="Raw ENI Loyalty Num")
    customer_type: OptionalInt
    actor_id: OptionalInt = Field(None, alias="Actor ID")
    client_id: OptionalString
    contract_name: OptionalString
    payout_day: OptionalString
    contract_id: OptionalString
    airport_id: OptionalString
    member_type: OptionalString
    is_refund_card: OptionalBool
    contract_number: OptionalString
    airport_code: OptionalString
    payed_value: OptionalFloat
    consumer_id: OptionalInt = Field(None, alias="Consumer ID")
    discount_card_id: OptionalString = Field(None, alias="Discount Card ID")
    discount_card_number: OptionalString
    discount_card_user_identity: OptionalString
    discount_card_physical_type_id: OptionalString = Field(None, alias="Discount Card Physical Type ID")
    discount_card_activation_date: OptionalString
    discount_card_expiration_date: OptionalString
    is_money: OptionalBool
    prepaid_card_current_regular_credit: OptionalString
    prepaid_credit_amount_charge: OptionalString
    prepaid_credit_transaction_charge: OptionalFloat = Field(
        None, alias="Prepaid Credit  Transaction Charge"
    )  # Extra space between words
    prepaid_card_current_revalue_credit: OptionalFloat
    prepaid_revalue_credit_amount_charge: OptionalFloat
    is_revalue_reward_transaction: OptionalBool
    prepaid_card_monthly_amount_credit_usage: OptionalString = Field(
        None,
        alias="Prepaid Card Monthly Amount Credit Usage ",
    )  # Extra space at the end
    prepaid_card_monthly_transactions_credit_usage: OptionalString = Field(
        None,
        alias="Prepaid Card Monthly Transactions Credit Usage ",
    )  # Extra space at the end
    loyalty_card_number: OptionalString
    campaign_id: OptionalInt = Field(None, alias="Campaign ID")
    campaign_type: OptionalInt  # Changed from String
    card_id: OptionalString = Field(None, alias="Card ID")
    machine_serial_number: OptionalString
    machine_id: OptionalInt = Field(None, alias="Machine ID")
    transaction_status_id: OptionalInt = Field(None, alias="Transaction Status ID")
    transaction_status_name: OptionalString = Field(None, alias="Transaction Status Name")
    device_transaction_id: OptionalInt = Field(None, alias="Device Transaction ID (DTID)")
    vendor_transaction_uid: OptionalString = Field(None, alias="Vendor Transaction UID (VUID)")
    card_bin: OptionalString = Field(None, alias="Card BIN")
    batch_ref_number: OptionalString
    operator_transaction_id: OptionalString = Field(None, alias="operator transaction id")
    retail_store_id: OptionalString
    retail_pos_id: OptionalString
    operator_data: OptionalString = Field(None, alias="Operator Data 1")
    credit_card_type: OptionalString
    original_authorization_time: OptionalString = Field(None, alias="original authorization time")
    is_deferred_transaction: OptionalBool

    products: list[NayaxProductSchema]


class NayaxTransactionSchema(NayaxBaseModel):
    transaction_id: OptionalInt = Field(None, alias="TransactionId")
    remote_start_transaction_id: OptionalString = Field(None, alias="RemoteStartTransactionId")
    payment_method_id: OptionalInt = Field(None, alias="PaymentMethodId")
    site_id: OptionalInt = Field(None, alias="SiteId")
    machine_time: OptionalDatetime = Field(None, alias="MachineTime")
    void: OptionalBool
    machine_id: OptionalInt = Field(None, alias="MachineId")

    data: NayaxDataSchema
