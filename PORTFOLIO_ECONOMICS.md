# Portfolio economics

**MANAGEMENT ESTIMATE · UNAUDITED · VENTURE-LEVEL VALUATION MODEL · NOT AN
INDEPENDENT APPRAISAL · NOT ATTRIBUTABLE PARENT NAV**

Every figure on this page is a management estimate produced by a
venture-level model. None of it is an audit, an appraisal, or a valuation of
Noaerth as an entity. Attributable parent NAV is **not established**.

---

## Source of record

| field | value |
| --- | --- |
| model | Noaerth portfolio economics |
| version | v0.2 |
| source type | `user_provided_management_model` |
| independent verification | **unavailable** |
| audited | no |
| attributable NAV established | **no** |
| currency | USD |

The figures were supplied by the owner. They are **not** the output of any
workbook, script or model file present in this repository or anywhere under
`/Users/matador/startups`; a search of the local portfolio for these counts and
values returned no matching model. They are recorded as owner-provided
management estimates, which is a weaker and more accurate claim than "model
output".

Machine-readable provenance:
[`data/portfolio-economics-v0.2.json`](data/portfolio-economics-v0.2.json)

---

## What is being counted

| stage | ventures |
| --- | --- |
| Live | 16 |
| Building | 102 |
| Research | 6 |
| **Registered total** | **124** |

The stage counts sum exactly to the registered total: 16 + 102 + 6 = 124.

"Live" and "Building" are stage labels. They are not verified operating
status, revenue, or customer counts.

---

## Scenarios

### Modeled gross venture value

| scenario | value |
| --- | --- |
| Low | $228.635M |
| Base | $653.243M |
| High | $2.80218B |

### Risk-adjusted, after a 25% portfolio overlap and correlation haircut

| scenario | value |
| --- | --- |
| Low | $171.476M |
| Base | $489.932M |
| High | $2.101635B |

### Arithmetic check

The haircut was verified rather than assumed:

| scenario | gross | × 0.75 | stated | delta |
| --- | --- | --- | --- | --- |
| Low | 228,635,000 | 171,476,250 | 171,476,000 | 250 |
| Base | 653,243,000 | 489,932,250 | 489,932,000 | 250 |
| High | 2,802,180,000 | 2,101,635,000 | 2,101,635,000 | 0 |

The low and base figures are rounded to the nearest thousand; the high figure
is exact. **The figures are internally consistent.**

Internal consistency is not verification. It shows the stated risk-adjusted
values follow from the stated gross values by the stated rule. It says nothing
about whether either is right.

---

## How the scenarios are built

Each venture is placed in a stage, then each stage carries a value band.
Scenarios differ by how much of each band is realised:

- **Low** assumes the floor of every stage band.
- **Base** assumes the midpoint.
- **High** assumes the ceiling, and assumes the venture stage advances as
  labelled.

The 25% haircut then removes the portion of value attributed to correlation
between ventures inside one portfolio: two ventures serving the same customer
are not worth the sum of their independent valuations, and summing 124
independent valuations assumes no shared costs, customers, staff or
liabilities anywhere.

The haircut is applied **uniformly to all three scenarios**. That is a
simplifying assumption, not a measurement. Real correlated exposure would
differ per venture and per stage.

---

## Limitations

These are the reasons not to treat the numbers as more than they are.

1. **No backing computation exists.** No workbook or script reproduces these
   figures. They currently cannot be recomputed by anyone, including the owner.
2. **The haircut is uniform, not measured.** A flat 25% across 124 ventures and
   three stages ignores that correlation is not evenly distributed.
3. **Venture value is not additive to parent value.** Summing 124 venture
   valuations assumes none of them share costs, customers, staff or liabilities.
4. **Attributable NAV is not established.** Ownership percentages across the
   124 ventures are undocumented. No figure here can be assigned to the parent
   entity.
5. **No external evidence supports the spread.** There is no traction, revenue,
   comparable-transaction, discount-rate or cost-basis evidence behind the
   scenario bands.
6. **Stage labels are not verified operating status.**

---

## Required language

Any public rendering of these figures — profile, repository, deck, or social
post — must carry all five labels:

- MANAGEMENT ESTIMATE
- UNAUDITED
- VENTURE-LEVEL VALUATION MODEL
- NOT AN INDEPENDENT APPRAISAL
- NOT ATTRIBUTABLE PARENT NAV

**Prohibited:** "Noaerth is worth $653M".

**Permitted:** "Portfolio model: $653.2M gross base scenario — management
estimate, unaudited, venture-level model, not an independent appraisal, not
attributable parent NAV."

---

## Geometry rule

Any generated financial graphic must be numerically honest. Bar or area length
is proportional to the stated value on a stated scale.

**No 3D volume, perspective or shadow may encode magnitude.** Perspective
exaggerates by construction: a bar drawn with depth reads larger than an equal
bar without, so a 2.8B high scenario rendered in pseudo-3D would imply a far
larger multiple than it represents. The scenarios differ by roughly 12× from low
to high, and the graphic must show that ratio rather than dramatise it.

---

## What would change this

Honest movement from management estimate toward something verifiable:

1. A model workbook or script that reproduces every figure from venture-level
   inputs, versioned and dated.
2. Documented ownership percentages per venture, which is the precondition for
   any attributable NAV statement.
3. A correlation-aware haircut derived from actual shared customers, costs and
   staff rather than a flat rate.
4. Third-party review of venture valuations against comparable transactions.

Until then the honest description of this work is: a portfolio-scale valuation
model run by management, on assumptions, unaudited, whose outputs are published
because the reasoning matters more than the precision.