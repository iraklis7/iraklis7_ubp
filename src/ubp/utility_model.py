from pydantic import BaseModel, Field


# Define your schema
class Utility_Bill(BaseModel):
    issuer_name:                    str = Field(description="Business full legal name issuing the invoice (usually "
                                                "contains 'Α.Ε.')")
    document_number:                str = Field(description="Invoice document number or alphanumberic sequence "
                                                "including a space")
    customer_id_number:             str = Field(description="Customer identification number (ΚΩΔΙΚΟΣ ΠΕΛΑΤΗ)")
    customer_name:                  str = Field(description="Customer's name. If nooe is found return [redacted]")
    customer_address:               str = Field(description="Customer's address (no newline chars, include postal "
                                                "code). If none is found, return [redacted]")
    customer_vat_number:            str = Field(description="Customer VAT number, usually denoted as 'ΑΦΜ' or "
                                                "'Α.Φ.Μ.'. If none is found, return [redacted]")
    customer_meter_number:          str = Field(description="Electricity meter number")
    bill_type:                      str = Field(description="Type of bill, 'Έναντι' or 'Εκκαθαριστικός' only, "
                                                "'None' otherwise")
    bill_pub_date:                  str = Field(description="Publication date in YYYY-MM-DD format")
    bill_period_start:              str = Field(description="Start date of the billing period in YYYY-MM-DD format")
    bill_period_end:                str = Field(description="End date of the billing period in YYYY-MM-DD format")
    bill_due_date:                  str = Field(description="Due date for the invoice payment in YYYY-MM-DD format")
    bill_total_fixed_charges:       float = Field(description="Total fixed charges on the invoice. Subtract any discounts "
                                                  "(usually refered to as 'Έκπτωση παγίου')")
    bill_vat_amount:                float = Field(description="Total VAT amount on the invoice (ΦΠΑ)")
    bill_refund_amount:             float = Field(description="Total refund amount on the invoice including minus sign, and "
                                                  "excluding fixed charges. If it does not exist, return 'None'")
    bill_total_amount:              float = Field(description="Total amount due on the invoice")


class Utility_Bill_Gas(Utility_Bill):
    commission_of_natural_gas:      float = Field(description="Commission of natural gas in euros (€)")
    distribution_of_natural_gas:    float = Field(description="Distribution of natural gas in euros (€)")
    transport_of_natural_gas:       float = Field(description="Transport of natural gas in euros (€)")
    usage_cubic_meters:             float = Field(description="Gas usage in cubic meters (Nm^3)")
    usage_kilowatt_hours:           float = Field(description="Gas usage in kilowatt hours (kWh)")
    rate_per_kilowatt_hour:         float = Field(description="Rate per kilowatt hour (€/kWh)")


class Utility_Bill_Power(Utility_Bill):
    commission_of_power_charges:   float = Field(description="Commission of power charges in euros (€)")
    adjustable_power_charges:      float = Field(description="Adjustable power charges in euros (€)")
    bill_fees_amount:               float = Field(description="Total fees amount on the invoice, like 'Τέλος', "
                                                  "'Ε.Τ.Μ.Ε.Α.Ρ.' and 'Ειδικός Φόρος Κατανάλωσης', but not 'increase'")
    usage_kilowatt_hours:           float = Field(description="Electricity usage in kilowatt hours (kWh)")
    rate_per_kilowatt_hour:         float = Field(description="Rate per kilowatt hour (€/kWh). Subtract any consistent "
                                                  "payment bonus, like 'Έκπτωση συνέπειας'")
    municipality_fee:               float = Field(description="Municipality fee in euros (€)")
    television_fee:                 float = Field(description="Television fee in euros (€) (ΕΡΤ), 'None' otherwise")


class Utility_Bill_Water(Utility_Bill):
    water_charges:                  float = Field(description="Water charges in euros (€)")
    sewage_charges:                 float = Field(description="Sewage charges in euros (€)")
    bill_fees_amount:               float = Field(description="Total fees amount on the invoice, like 'Τέλος'")
    usage_cubic_meters:             float = Field(description="Water usage in cubic meters (m^3)")
