---
name: fintech
description: Financial technology domain context — regulatory frameworks, payment rails, compliance requirements, and competitive landscape patterns
applies-to-stages: [1, 2, 3, 4]
---

## Regulatory Context

When analyzing a fintech idea, consider these regulatory dimensions:

- **Money Transmission**: Most jurisdictions require money transmitter licenses (MSB registration with FinCEN in the US, state-level MTLs, or equivalent in other countries). Research the specific requirements for the target geography.
- **KYC/AML Compliance**: Know Your Customer and Anti-Money Laundering regulations are mandatory. Consider CDD (Customer Due Diligence), EDD (Enhanced Due Diligence), and ongoing transaction monitoring.
- **PCI DSS**: If handling payment card data, PCI DSS compliance is required. Consider tokenization and using payment processors that handle PCI scope.
- **Data Protection**: Financial data is subject to enhanced privacy requirements (GDPR for EU, CCPA for California, LGPD for Brazil, etc.).
- **Licensing Timeline**: Most financial licenses take 3-12 months to obtain. Factor this into feasibility and timeline assessments.

## Payment Rails & Infrastructure

- **Domestic transfers**: ACH (US), SEPA (EU), Faster Payments (UK), PIX (Brazil), local equivalents
- **International transfers**: SWIFT, correspondent banking, blockchain rails
- **Card networks**: Visa, Mastercard — interchange fees typically 1.5-3%
- **Mobile money**: M-Pesa, local mobile wallet systems
- **BaaS vs. Direct**: Banking-as-a-Service providers (Unit, Synapse, Bond) vs. obtaining your own banking charter — evaluate build vs. buy for financial infrastructure

## Competitive Landscape Patterns

- Traditional banks (high trust, slow innovation, high fees)
- Neobanks (Chime, Revolut, Nubank — digital-first, lower fees)
- Payment processors (Stripe, Square, Adyen — infrastructure providers)
- Money transfer operators (Western Union, MoneyGram — established networks)
- Fintech startups in the same corridor or segment

## Business Model Considerations

- Transaction fees are the most common revenue model (0.5-3% per transaction)
- FX margins for cross-border (0.5-2% above mid-market rate)
- Subscription models for premium features
- Float revenue on held balances
- Interchange revenue for card programs
- Unit economics are critical — most fintech startups are unprofitable for 2-4 years
