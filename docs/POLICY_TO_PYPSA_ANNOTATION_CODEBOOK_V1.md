# Policy-to-PyPSA Annotation Codebook v1.0

**发布日期：2026-11-27｜状态：PROPOSED — 人工标注规程草案，非 Gold Standard。**

**项目：** EnergyPolicy-LLM — Evidence-Grounded Policy-to-Model  
**当前适用材料：** 冻结的 `NM_COOP_2025.txt`（17.9.571 NMAC；source SHA-256 `673f60931b4a2ba68c2de2c67601097bc292da8998536bdb38b3d014acfdea01`）、`NM_2025_Policy_to_PyPSA_Reviewed_AI_Draft_Blind_Annotation.xlsx`。  
**范围：** 当前 **14 条原审核任务 + 12 条新增初始任务**，并非 26 条已确认的独立法律义务。14 章节、167 个关键词候选行属于不同计数层级。两位独立人工标注者与裁决尚未完成，`gold_count=0`。

> **阅读顺序：** A 单位与证据 → B 法律语义 → C PyPSA 编译 → D 争议/质量 → E 工作流程 → F 示例。**不可用 AI 建议填充 Reviewer A/B 或最终人工裁决栏。**

## 1. 标注对象及拆分单位

| 层级 | 定义 | 唯一标识 | 可作为训练/评测实例？ |
|---|---|---|---|
| Source snapshot | 带版本、获取时间、完整 SHA-256 的冻结官方原文 | `source_id + sha256` | 作为证据源 |
| Section | 如 17.9.571.8；包含多个段落、交叉引用和修订沿革 | `source_id + section` | 仅用于检索分组 |
| Candidate line | 正则/关键词找到的文本行（本源 167 行） | 字符偏移 | **不是自动 gold** |
| Review task | 待检查的一组条款或话题（当前 26 条） | `Case_ID` | 可做审核工作项，不等于独立义务 |
| **Atomic legal proposition** | 具有单一义务/许可/定义/条件的最小可独立判断的法律陈述；保留必要条件和交叉引用 | `annotation_id` | **经双人独立标注+真实裁决后**可做 gold |
| Model mapping candidate | 对明确的 `model_profile_id` 提出的 PyPSA/外部核算转译 | `annotation_id + model_profile_id` | 可做编译评测；不可代替法律标注 |

**拆分标准**：不同主体、行动、比例、年份、责任分配、例外、证书所有权/转移/注销、报告义务分开；同一法律要求的限定条件必须随记录保存。跨条款组合需 `depends_on_annotation_ids`。禁止以物理行、一个章节、一个百分比直接代表一个完整法律义务。

## 2. 字段字典：身份、原文证据和审阅来源

| 字段 | 数据类型 / 允许值 | 说明及判定规则 |
|---|---|---|
| `annotation_id` | 唯一字符串，例如 `NM25-008-TARGET` | 每个原子命题一个 ID；保留 `parent_case_id` 关联旧工作项 |
| `parent_case_id` | 现有 `NM25-001...026` | 回溯 Excel；新拆出的规则可用后缀 |
| `source_id` / `rule_version` | `NM_COOP_2025` / 官方版本文字 | 不得以标注日期替代法规生效/修改日 |
| `source_sha256` | 64 位 SHA-256 | 必须等于冻结 UTF-8 原文的哈希 |
| `provision` / `subsection` | 例 `17.9.571.8`, `B`, `F(2)` | 精确到可识别的最小款项；不要自动修正原文交叉引用 |
| `start_char`, `end_char` | 非负整数，**0-based end-exclusive** | Python 字符位置；必须满足 `text[start:end] == exact_text`；不包括无关沿革注 |
| `exact_text` | 原文精确字符串 | 证据而非释义；可能跨行，保持冻结文件的空白 |
| `evidence_role` | `PRIMARY` / `DEFINITION` / `CROSS_REFERENCE` / `CONDITION` / `EXCEPTION` | 一条规则可有多段证据，分别存 `evidence_spans[]` |
| `source_verification` | `MATCHED` / `MISMATCH` / `NOT_CHECKED` | 文本核对结果**不等于**政策含义已裁决 |
| `annotation_origin` | `AI_SUGGESTION` / `HUMAN_A` / `HUMAN_B` / `ADJUDICATED` | 必须在每份产物中明确来源，不能混写 |
| `field_status` | `VERIFIED` / `REQUIRES_CORRECTION` / `INSUFFICIENT_EVIDENCE` / `NOT_APPLICABLE` | **缺失 != 零**；不适用用 null + NOT_APPLICABLE |

**特殊原文复核已知事项**：旧 NM25-012 和 NM25-014 的证据 `end_char` 应分别为 **7857**、**10357**，避免纳入修订沿革；旧 NM25-007 的 `17.9.571.8(A)` 不是比率条款，`denominator=null`。修改必须重新验证文本切片。

## 3. 法律含义标注字段（独立于模型能力）

| 字段 | 允许值/格式 | 定义与填写规则 |
|---|---|---|
| `legal_semantic_type` | 主标签见 3.1 | 最主要的法律功能；复合句需拆分，必要时另设 secondary types |
| `normative_force` | `MUST` / `MUST_NOT` / `MAY` / `DEFINITION` / `CONDITIONAL_MUST` / `REPORTS` / `UNKNOWN` | 区分强制、许可、条件性要求和解释性定义；不要把 MAY 写成 MUST |
| `obligated_entity` | `cooperative` / `distribution_cooperative` / `generation_transmission_cooperative` / `utility` / `other` / `UNKNOWN` | 用受控词表；G&T 对成员供电的责任应根据 8(F)(2)、9(B) 附交叉引用，不可统一替换直接主体 |
| `regulated_action` | 自由文本+受控动作 | 例如达到 RPS、注销 REC、判定年度成本、提交报告、保留记录 |
| `target_fraction` | 0–1 或 null | `0.40`、`0.50`、`0.80`、`1.00`；不是 `40`，无比例填 null |
| `target_date` | ISO `YYYY-MM-DD` 或 null | 要区分截止日期、规则版本日期、报告提交日、适用年度 |
| `date_role` | `DEADLINE` / `PERIOD_START` / `ANNUAL_FILING_DUE` / `HISTORICAL_CUTOFF` / `EFFECTIVE_DATE` / `UNKNOWN` | 同一天可有不同法律含义；不以文件发布日期替代目标日 |
| `compliance_period` | `CALENDAR_YEAR` / `PLAN_YEAR` / `MULTIYEAR` / `UNKNOWN` / null | 只有文本明确或合法交叉引用支持时才标；plan year 的定义本身**不证明**存在申报窗口 |
| `numerator_metric` | `ELIGIBLE_RENEWABLE_ENERGY_MWH` / `ZERO_CARBON_ELECTRICITY_MWH` / `QUALIFYING_RECS_MWH_EQUIV` / `OTHER` / null | 分子须记录资格和证书核算条件；8(A) 本身无比率 |
| `denominator_metric` | `NM_TOTAL_RETAIL_SALES_MWH` / `NM_RETAIL_ELECTRICITY_SUPPLIED_MWH` / `GENERATION_MWH` / `OTHER` / null | 不能凭主观解释互换法律措辞；标准化需映射表与证据 |
| `rec_accounting` | `RETIREMENT` / `OWNERSHIP` / `TRANSFER` / `BANKING` / `TRACKING` / `NONE` / `UNKNOWN` | 可多选；8(A) 的 REC 注销与 11 章细节分开 |
| `eligibility_conditions` | 条件数组或 null | 资源、时间资格、权属、例外；不得只写模糊“合规” |
| `condition_logic` | `ALL` / `ANY` / `IF_THEN` / `NONE` / `UNKNOWN` + 每个条件 | 2050 条款的三项门槛必须记录为同时满足，不能直接编译为无条件 80%/100% |
| `exceptions` | `exception_type` + 子款证据 | 豁免、合理成本门槛等必须独立可审计 |
| `monetary_threshold` | 数值 + `USD/MWh` + 年份基准 | 例如 60 USD/MWh，需记录 CPI 更新和计价位置；绝不写入 RPS 分子/分母 |
| `decision_maker` | 原文明确的角色或 `UNKNOWN` | 10(A) 由合作社自行逐年判定；11 章被动语态不能擅自指定 G&T 为验证者 |
| `source_ambiguity` | `NONE` / `CROSS_REFERENCE_MISMATCH` / `UNDEFINED_TERM` / `TEMPORAL_AMBIGUITY` / `OTHER` | 11(D)/(H) 疑似引用 13 章的内部条款，保留原文，标争议，不自动改为 11 章 |

### 3.1 法律语义类型（主标签）

| Label | 判定定义 | 本源正例 | 反例/注意 |
|---|---|---|---|
| `DEFINITION` | 解释术语、主体类别或核算对象，不单独设立数值目标 | 17.9.571.7 合作社类型定义 | 不应因为非直接可执行就写“无用” |
| `TARGET` | 给出有约束力的数值/比例/时间目标 | 8(B) 2025 年 40%；8(C) 2030 年 50% | 8(A) 只有合规方式，无独立比例 |
| `CONDITIONAL_TARGET` | 法定义务受明示条件限制 | 8(D) 2050 年 80%；9(A) 2050 年 100% zero carbon | 不得无条件生成硬约束 |
| `ACCOUNTING` | 合规核算、REC 注销/记账/转移/结转要求 | 8(A) 与 11 | 不是简单可再生机组容量约束 |
| `ELIGIBILITY` | 规定哪些主体、资源或历史设施可计入合规 | 8(E) 2008 历史资源 | 不等于“所有存量资源” |
| `RESPONSIBILITY` | 将某项法律责任在合作社/G&T 之间分配 | 8(F)(1)–(3)；9(B) | assigned 的是 renewable energy，非必然 REC |
| `COST_EXCEPTION` | 指明成本触发的例外或限制 | 10(A) 60 USD/MWh 并按规则调整 | 不是 RPS ratio；自行判定条件不可遗漏 |
| `PERMISSION` | 允许一种行动而非强制采取 | 10(B) 自愿承担高于门槛的成本 | 不应编译成强制支出 |
| `REPORTING` | 报告义务、截止日、提交内容 | 13(A) 每年 4 月 30 日前报告上一日历年情况 | 报告日不是 RPS 目标日 |
| `OTHER` | 无法归入上述但确为规则 | 必须书面说明 | 不得用作跳过困难条款 |

## 4. PyPSA 编译标签体系（与法律标注分开）

### 4.1 编译角色 `compilation_roles[]`（多选）

| Label | 含义 | 示例 | 输出 |
|---|---|---|---|
| `ENTITY_MAPPING` | 将法定义务主体映射到模型的 utility / BA / bus / load 集合 | G&T→member distribution coops | `entity_map`；不自动建立比例约束 |
| `PARAMETER` | 提供比例、时间、成本系数、技术条件等 | 50%、2030、60 USD/MWh | 参数表、单位及作用范围 |
| `OPTIMIZATION_CONSTRAINT` | 根据**已验证的**模型变量形成直接 LP/MILP 限制 | 某些明示容量限制 | 必须记录方程、单位与适用时间 |
| `ACCOUNTING_CONSTRAINT` | 需要外部/扩展合规账本等式或不等式 | 零售售电量、REC 注销 | `rec_ledger` + retail sales；不等价于本地发电 |
| `ELIGIBILITY_RULE` | 筛选符合政策计入条件的技术/资源/证书 | 8(E) grandfathered resources | eligible set 与证据 |
| `CONDITIONAL_LOGIC` | 根据条件决定法律义务是否激活 | 8(D)/9(A) 2050 目标 | `all_conditions`、资料依赖、未满足时动作 |
| `COST_EXCEPTION_LOGIC` | 成本上限的计算、触发、放松 | 10(A) | 基准年、CPI、LCOE、判定主体 |
| `REPORTING_ONLY` | 需要单独输出报告，不改变核心优化约束 | 13(A) | compliance report |
| `DEPENDENCY_ONLY` | 为其他条款提供解释，不独立编译 | 定义条款 7 | ontology/依赖图 |
| `UNRESOLVED` | 编译语义/依赖不能确定 | 错误交叉引用、缺少 REC 数据 | 阻止自动部署 |

**强调：** 编译角色不是可执行性；某条定义可以是 `ENTITY_MAPPING` + `DEPENDENCY_ONLY`，即使 `executability=NOT_DIRECTLY_EXECUTABLE`。

### 4.2 可执行/安全决策（**须指定模型配置**）

| `executability` | 判定要求 | `legal_equivalence` |
|---|---|---|
| `LEGAL_CONSTRAINT` | 有经裁决法律字段、完整主体/分母/REC/时间口径和所需变量；可执行且含义一致 | 仅在证明等价时 true |
| `SCENARIO_PROXY` | 有合理、明示但**非法律等价**的代理模型；标出差异/假设/误差解释 | **false** |
| `ABSTAIN` | 法律歧义、关键数据缺失、条件判断不能落实，拒绝自动生成此约束 | false |
| `NOT_DIRECTLY_EXECUTABLE` | 定义/报告/责任本身不是单个优化约束，但可能有下游用途 | 不适用（null） |
| `UNASSESSED` | 尚无 `model_profile_id` 或未开展编译检查 | null |

**须同时填 `model_profile_id`、`compiler_version`、`missing_dependencies[]`、`mapping_assumptions[]`、`equivalence_rationale`。** 法律意义应在模型配置变化后保持不变，执行决策则可以改变。优先分别记录 **legal status** 和 **model readiness**，不以 `SCENARIO_PROXY` 覆盖法律标签。

### 4.3 核算数学形式（仅供编译审核的候选表达式）

对于经审核的适用主体 `u` 和合规年度 `y`，概念性 RPS 候选约束：

```text
retired_eligible_REC_MWh_equivalent[u,y] >= target_fraction[y] * NM_retail_sales_MWh[u,y]
```

需确认证书注销与可计入 MWh 的法律关系、责任供电、余额结转、可用证书资格、豁免以及时间口径；这**不是**可以直接在 PyPSA 中使用的经法律确认公式。**禁止**未经说明将其替换为 `local_renewable_generation / local_total_generation >= target`，后者至多属于代理情景。

## 5. 质量标签、人工盲审与 Gold 冻结

| 字段 | 允许值 | 使用说明 |
|---|---|---|
| `annotation_status` | `AI_DRAFT` / `READY_FOR_BLIND_REVIEW` / `A_COMPLETE` / `B_COMPLETE` / `DISAGREEMENT` / `ADJUDICATED` / `BLOCKED_SOURCE_AMBIGUITY` | 只有真实 A/B 独立审阅与真实裁决方可进入 ADJUDICATED |
| `reviewer_a_id`, `reviewer_b_id` | 不同的真实审阅者 ID | AI 不能模拟两名独立审阅人 |
| `review_a_labels`, `review_b_labels` | 独立填写完整字段，不读取 AI 草案/对方意见 | 对身份、比例、分母、REC、条件、证据位置及模型决定逐项核查 |
| `adjudicator_id` | 真实裁决人 ID | 解决冲突、写明采取/拒绝的解释 |
| `disagreement_type` | `NONE` / `SPAN` / `ENTITY` / `METRIC` / `DATE` / `MODALITY` / `CONDITION` / `REC` / `COMPILATION` / `OTHER` | 可多选，记录双方差异 |
| `confidence` | `HIGH` / `MEDIUM` / `LOW` | 仅辅助排审，不是概率、不能免裁决 |
| `gold_eligible` | `true` / `false` | 必须满足来源、独立审核、裁决、证据及持久化检查 |
| `split_group_id` | 政策文件/政策工具/修订家族 ID | 实验中同一法规及近重复条款应在同一 train/test 分组，禁止泄漏 |

**盲审流程**：1) 证据导出且隐藏 `AI建议_非人工`、AI预填意见、另一位审阅人；2) Reviewer A/B 各自完成法律语义与源证据；3) 比较不一致并记录；4) 第三位人员/指定裁决者基于原文决定；5) 最终由独立编译审核者在指定模型配置上评价可执行性；6) 冻结版本和 hold-out 分组后再测试模型。用户对冻结原文“文本一致性已核对”只能填 `source_verification=MATCHED`，不能标注为 `ADJUDICATED`。

## 6. 具体示范（全部为 AI 编写的教学示例，**不是最终人工 Gold**）

| 法律位置 | 原子命题/关键字段 | 语义标签 | 编译角色 | 关键缺口与注意 |
|---|---|---|---|---|
| **8(A)** | 分配合作社通过注销 REC 展示供电组合满足 RPS；**无独立百分比分母** | ACCOUNTING | ACCOUNTING_CONSTRAINT | 旧 NM25-007 必须 `denominator=null` |
| **8(B)** | 2025-01-01：40% 的 NM 零售售电量 | TARGET | PARAMETER + ACCOUNTING_CONSTRAINT | 交叉引用 8(F)(2) 的 G&T 供电责任，不等于本地机组出力 |
| **8(C)** | 2030-01-01：50% 的 NM 零售售电量 | TARGET | PARAMETER + ACCOUNTING_CONSTRAINT | 必须保留 retail sales 和 REC 的独立核算 |
| **8(D)** | 2050-01-01：80%，且原文三项条件需共同满足 | CONDITIONAL_TARGET | PARAMETER + CONDITIONAL_LOGIC | 按条件核对；不得硬编码无条件目标 |
| **8(F)(1)** | G&T 给成员配电合作社分配 **renewable energy** | RESPONSIBILITY | ENTITY_MAPPING + ACCOUNTING_CONSTRAINT | 不得改写成必然分配 REC |
| **8(F)(3)** | 采用被动语态的核验/责任表述 | RESPONSIBILITY | ACCOUNTING_CONSTRAINT | “由 G&T 核验”需明确为推断而非原文 |
| **9(A)** | 2050 年 NM 零售客户 100% zero-carbon electricity，受三项条件限制 | CONDITIONAL_TARGET | PARAMETER + CONDITIONAL_LOGIC | **zero carbon ≠ renewable**，不可合并 80% 与 100% |
| **10(A)** | 合作社逐年判定大于 60 USD/MWh 的成本门槛，2020 年后按规定通胀更新 | COST_EXCEPTION | COST_EXCEPTION_LOGIC + PARAMETER | `monetary_threshold` 单独列，`numerator=null`, `denominator=null` |
| **10(B)** | 可自愿承担高于合理门槛成本 | PERMISSION | CONDITIONAL_LOGIC | MAY != MUST |
| **11** | REC 权属、协议转移、结转与追踪（按实际原子规则拆开） | ACCOUNTING / ELIGIBILITY | ACCOUNTING_CONSTRAINT / ELIGIBILITY_RULE | 对 11(D)/(H) 中疑似错误指向 13 章的引用保留 `CROSS_REFERENCE_MISMATCH` |
| **13(A)** | 每年 4 月 30 日前提交前一日历年报告 | REPORTING | REPORTING_ONLY | `date_role=ANNUAL_FILING_DUE`；不是 RPS 达标日 |

**术语使用注意：** 上表“分配合作社”应统一为 **配电合作社**（distribution cooperative）。原文 RPS 的 `NM_total_retail_sales` 是法定分母；在缺乏定义证据的情况下，不允许用 `electric_energy_supply_portfolio` 或本地发电量替代。为避免误读，未来版本统一使用“配电合作社”。

## 7. JSON 结构示例（draft, not gold）

```json
{
  "annotation_id": "NM25-009-TARGET",
  "parent_case_id": "NM25-009",
  "source_id": "NM_COOP_2025",
  "source_sha256": "673f60931b4a2ba68c2de2c67601097bc292da8998536bdb38b3d014acfdea01",
  "provision": "17.9.571.8(C)",
  "legal_semantic_type": "TARGET",
  "normative_force": "MUST",
  "obligated_entity": "distribution_cooperative",
  "target_fraction": 0.50,
  "target_date": "2030-01-01",
  "date_role": "DEADLINE",
  "numerator_metric": "ELIGIBLE_RENEWABLE_ENERGY_MWH",
  "denominator_metric": "NM_TOTAL_RETAIL_SALES_MWH",
  "rec_accounting": ["RETIREMENT"],
  "depends_on_provisions": ["17.9.571.8(A)", "17.9.571.8(F)(2)", "17.9.571.11"],
  "compilation_roles": ["PARAMETER", "ACCOUNTING_CONSTRAINT", "ENTITY_MAPPING"],
  "model_profile_id": "UNSET",
  "executability": "UNASSESSED",
  "legal_equivalence": null,
  "annotation_origin": "AI_SUGGESTION",
  "annotation_status": "AI_DRAFT",
  "gold_eligible": false
}
```

**示例提醒：** 这里的 `numerator_metric` 是待核对的标准化语义抽象，`depends_on_provisions` 是人工复核建议，不能把它们理解为已经通过所有条款交叉解释。源证据 `start_char` / `end_char` 应从当前冻结文件精确导出，并附相应 `exact_text`，不得臆造偏移。

## 8. 工作簿对照和版本兼容

- **现有 `政策标注主表`（14 条）：** A–P 原预填/证据；Q–AB 人工审核、裁决栏必须**保持空白直至真实审核**。
- **现有 `AI建议_非人工`：** 仅供草案整理、**不进入盲审输入**。
- **现有 `PyPSA编译映射`：** 对接 `legal_semantic_type` / `compilation_roles` / `executability`；其中原先的 `NOT_DIRECTLY_EXECUTABLE` 属于“该条款不是单独优化约束”，不能当作法律错误。
- **现有 `新增条款待审_9_11_13`（12 条）：** 目前为章节/子款级任务，尚需细分、提取准确证据偏移、完成审核。
- **推荐新增的列/表：** `Atomic_Obligations`, `Evidence_Spans`, `Blind_Reviewer_A`, `Blind_Reviewer_B`, `Adjudication`, `Model_Profiles`, `Compiler_Decisions`, `Codebook_Version`。
- **与现有 Python 代码兼容性：** `src/energy_policy_llm/schema.py` 仍是简化的 `PolicyTarget` 数据结构，`compiler.py` 只实现生成份额语义安全门，**尚不能直接存储/执行本 Codebook 的全部标签，也没有完整的 PyPSA/REC 引擎**。本 Codebook 是**提议的标注规范**，不是声称已部署的 API Schema。

## 9. 标注质量验收条件

1. **来源正确**：每项有冻结来源、哈希、子款、原文证据和可复算偏移。
2. **义务粒度正确**：无两个互相独立的义务塞进同一个训练实例；限制条件完整。
3. **字段完整**：角色、动词/规范强度、对象、数值单位、日期角色、必要的 REC/成本/条件信息。
4. **标准化无越权**：不擅自把 renewable 改为 zero carbon、retail sales 改为 generation、assigned energy 改为 assigned REC。
5. **分工隔离**：两位真实审核者独立输入；AI 草案与裁决完全分离。
6. **模型依赖明确**：所有编译决定绑定具体模型配置、变量、数据、单位、时间范围及输出模式。
7. **拒绝策略可解释**：不确定项标 UNKNOWN/null 并说明原因，避免无依据的“强制法律等价”。
8. **版本可复现**：记录 codebook 版本、标注人、日期、变更记录；按法规家族冻结训练/测试切分。

## 10. 版本变更控制

当前版本 `v1.0` 仅制定标签定义和工作流；后续若发现字段不能无损表示 17.9.571 具体法律要求，必须更新 codebook 版本、附迁移规则，**不能悄然改写已裁决标签**。优先实证测试 8(F) 责任分工、9(A) 条件、10(A) 成本门槛、11(D)/(H) 原文引用歧义。独立裁决完成之前，所有示例均为非 gold。
