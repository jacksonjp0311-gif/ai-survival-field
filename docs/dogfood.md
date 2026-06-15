# Dogfood

Dogfood runs ASF-R against its own fixtures.

It verifies:

- bounded draft can pass,
- unsafe release fails closed,
- repair replay passes,
- closure validation can pass against exact synthetic evidence,
- no mutation is performed.

Dogfood is operational contact, not production proof.
