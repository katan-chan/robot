# Knowledge base (knowledge graph) của dự án

Graph nối **quyết định → thành phần → task → kiểm tra → vai trò agent → file**. Nhờ vậy, khi đổi một chỗ, agent biết ngay chỗ nào khác bị ảnh hưởng.

| File | Vai trò |
|---|---|
| [ontology.toml](ontology.toml) | Schema: loại nút, loại quan hệ (domain → range), câu hỏi năng lực CQ1–CQ12 |
| [curated.toml](curated.toml) | Phần biên soạn tay: thành phần, kiểm tra, vai trò, quan hệ ngữ nghĩa, bí danh |
| `graph.json` | Kết quả sinh tự động. **Không sửa tay** |
| [../../tools/kb.py](../../tools/kb.py) | Pipeline + lệnh truy vấn |

## Pipeline (theo graph-engineering)

```mermaid
flowchart LR
  O[ontology.toml<br/>schema + CQ] --> X
  D[docs/decisions/*.md] -->|luật: bảng quyết định,<br/>task, SUPERSEDES, CITES| X[trích xuất]
  C[curated.toml] -->|biên soạn tay| X
  H[harness.toml] --> X
  X --> F[gộp bí danh<br/>fusion]
  F --> V{kiểm domain/range,<br/>cạnh treo, một người ghi,<br/>nhãn trùng}
  V -->|lỗi| E[báo agent sửa nguồn<br/>hook exit 2]
  V -->|ok| G[graph.json]
  G --> Q[impact / deps / path / show / find]
```

## Schema rút gọn

```mermaid
graph LR
  Decision -- CONSTRAINS --> Component
  Decision -- SUPERSEDES --> Decision
  Decision -- CITES --> Decision
  Check -- VERIFIES --> Decision
  Check -- CHECKS --> Component
  Task -- IMPLEMENTS --> Component
  Task -- DEPENDS_ON --> Task
  Task -- PART_OF --> Phase
  Question -- BLOCKS --> Task
  AgentRole -- PERFORMS --> Task
  AgentRole -- REVIEWS --> Task
  AgentRole -- WRITES --> File
  Component -- STORED_IN --> File
  HarnessComponent -- STORED_IN --> File
  Bug -- AFFECTS --> Component
  Lesson -- ADDS_RULE_TO --> HarnessComponent
```

## Ví dụ: đổi danh mục servo (12.7) thì ảnh hưởng gì?

```mermaid
graph LR
  D127[12.7 danh mục servo] -- CONSTRAINS --> SC[comp:servo-catalog]
  ST[check:static-torque] -- CHECKS --> SC
  JT[check:jitter] -- CHECKS --> SC
  AS[check:actuator-saturation] -- CHECKS --> SC
  T11[T1.1 file tham số] -- IMPLEMENTS --> SC
  T12[T1.2 sinh model] -- DEPENDS_ON --> T11
  T14[T1.4 tư thế đứng] -- IMPLEMENTS --> ST
  T18[T1.8 bộ kiểm tra] -- IMPLEMENTS --> AS
```

Lệnh tương ứng: `uv run tools/kb.py impact 12.7`

## Chất lượng (lần dựng đầu, 2026-10-20)

- 235 nút, 428 cạnh (gồm Bước 15). `selftest` qua đủ CQ1–CQ12.
- Lấy mẫu 50 cạnh CITES do luật trích xuất: 50/50 đúng. Lỗi đã sửa trong luật: số phiên bản ("Blender 5.2") bị nhận nhầm là mã quyết định.
- Bug và Lesson đã có trong schema nhưng chưa có dữ liệu. Thêm khi có bug hoặc bài học đầu tiên.
