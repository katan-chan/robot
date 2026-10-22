# Cổng G1 — xem model 3D và các bộ phận

Model nguồn: [`models/spider.blend`](../../../models/spider.blend). Model MuJoCo dựng từ bản export của file này (`tools/blender export` → `build/model/` → `spider/model/build.py`).
Quyết định liên quan: 16.2, 16.3, 18.3. Ảnh tham khảo: [spider-reference.png](../spider-reference.png).

## Ảnh Blender và MuJoCo

Blender lưu model ở tư thế 0 (chân duỗi ngang). Ảnh MuJoCo `home` cũng ở tư thế 0, dùng để so với Blender. Ảnh `stand` là tư thế đứng.

| Góc | Blender (tư thế 0) | MuJoCo `home` | MuJoCo `stand` |
|---|---|---|---|
| Trước | ![](blender/front.png) | ![](mujoco-home/front.png) | ![](mujoco-stand/front.png) |
| Bên | ![](blender/side.png) | ![](mujoco-home/side.png) | ![](mujoco-stand/side.png) |
| Trên | ![](blender/top.png) | ![](mujoco-home/top.png) | ![](mujoco-stand/top.png) |
| Chéo | ![](blender/iso.png) | ![](mujoco-home/iso.png) | ![](mujoco-stand/iso.png) |

Ảnh trước và ảnh bên giống nhau vì 4 chân xếp chữ X đối xứng.
MuJoCo chưa tô màu từng bộ phận, mọi geom có màu xám. Màu chỉ có ở Blender.

## Bảng thành phần

In bằng `uv run python -m spider.sim.view --parts`. Khối lượng đọc từ MuJoCo (`m.body_mass`, `mj_getTotalmass`). Cấu hình B (19.3), servo DS3235/DS3240 (19.4, thông số ước lượng), tải 2 kg (19.6).

| body | parent | joint | range (deg) | servo | mass (g) | geoms |
|---|---|---|---|---|---|---|
| torso | world | root | - | - | 598.9 | torso_mesh, fl_hip_yaw_servo, fr_hip_yaw_servo, rl_hip_yaw_servo, rr_hip_yaw_servo, torso_geom |
| fl_coxa | torso | fl_hip_yaw | -60 .. 60 | DS3235 | 72.7 | fl_coxa_mesh, fl_hip_pitch_servo |
| fl_femur | fl_coxa | fl_hip_pitch | -90 .. 90 | DS3240 | 77.1 | fl_femur_mesh, fl_knee_servo |
| fl_tibia | fl_femur | fl_knee | -30 .. 150 | DS3235 | 19.3 | fl_tibia_mesh, fl_foot_geom |
| fr_coxa | torso | fr_hip_yaw | -60 .. 60 | DS3235 | 72.7 | fr_coxa_mesh, fr_hip_pitch_servo |
| fr_femur | fr_coxa | fr_hip_pitch | -90 .. 90 | DS3240 | 77.1 | fr_femur_mesh, fr_knee_servo |
| fr_tibia | fr_femur | fr_knee | -30 .. 150 | DS3235 | 19.3 | fr_tibia_mesh, fr_foot_geom |
| rl_coxa | torso | rl_hip_yaw | -60 .. 60 | DS3235 | 72.7 | rl_coxa_mesh, rl_hip_pitch_servo |
| rl_femur | rl_coxa | rl_hip_pitch | -90 .. 90 | DS3240 | 77.1 | rl_femur_mesh, rl_knee_servo |
| rl_tibia | rl_femur | rl_knee | -30 .. 150 | DS3235 | 19.3 | rl_tibia_mesh, rl_foot_geom |
| rr_coxa | torso | rr_hip_yaw | -60 .. 60 | DS3235 | 72.7 | rr_coxa_mesh, rr_hip_pitch_servo |
| rr_femur | rr_coxa | rr_hip_pitch | -90 .. 90 | DS3240 | 77.1 | rr_femur_mesh, rr_knee_servo |
| rr_tibia | rr_femur | rr_knee | -30 .. 150 | DS3235 | 19.3 | rr_tibia_mesh, rr_foot_geom |
| payload | torso | - | - | - | 2000.0 | payload_geom |

**Robot không tải: 1275.6 g** (ngân sách 1.10–1.45 kg, 19.7). **Có tải: 3275.6 g** (giới hạn 3.5 kg).

Thân 598.9 g gồm tấm thân PLA, 4 servo `hip_yaw` (DS3235, 65 g mỗi cái theo danh mục) và 200 g pin LiPo 2S + mạch (`torso_extra_mass`, 19.5). Hàng `payload` lấy khối lượng khai báo trong `physics.toml`; MuJoCo cộng nó vào body `torso` (geom hộp 0.15 × 0.12 × 0.05 m giữa mặt trên thân, không va chạm).

## Điều đã đổi so với bản G1 trước

- **Cấu hình B thay bản nhỏ (19.3):** thân 0.20 × 0.16 × 0.010 m (trước 0.10 × 0.08), coxa/femur/tibia 0.05/0.09/0.12 m (trước 0.03/0.055/0.075), bàn chân bán kính 12 mm. Bản trước nặng 330.3 g với servo MG90S, không mang được tải 2 kg.
- **Servo theo loại khớp (19.4):** `hip_pitch` DS3240 (3.92 N·m), `hip_yaw` và `knee` DS3235 (3.4 N·m). Thông số là ước lượng ở khoảng 6 V, cần hiệu chỉnh khi có servo thật (13.4).
- **BUG-001** ([docs/bugs/BUG-001.md](../../bugs/BUG-001.md)): ma sát bàn chân trước đây không có tác dụng; nay mọi tiếp xúc sàn–bàn chân có μ = 0.9.
- **BUG-002** ([docs/bugs/BUG-002.md](../../bugs/BUG-002.md)): chân bò 33 mm dưới lực ngang bằng nửa giới hạn ma sát; nay < 0.5 mm. Bộ giải dùng nón ma sát elliptic, `impratio = 10`, `noslip_iterations = 10`, chạy chậm hơn khoảng 28% (vẫn nhanh hơn thời gian thực khoảng 115 lần).

## Số liệu kiểm vật lý (physics-verifier và test, có tải 2 kg)

Mọi số đọc từ MuJoCo. Tỉ lệ là mô-men khớp chia mô-men cực đại của servo; ngưỡng 0.5 (10.5, 14.5).

| Kiểm tra | Cách đo | Kết quả |
|---|---|---|
| Đứng 4 chân `stand` | giữ 3 s, `actuator_force` | hip_pitch 0.11, knee 0.07, hip_yaw 0.002. Thân cách sàn 72 mm |
| Đứng 3 chân (19.8) | nhấc lần lượt từng chân 40 mm (thực tế lên 24 mm do servo lún), `mj_inverse` ở tư thế đã ổn định | hip_pitch **0.448**, knee 0.235, hip_yaw 0.014. Qua, biên còn 0.052 |
| Đứng 3 chân | cùng tư thế, mô phỏng giữ 1.5 s, `actuator_force` | hip_pitch 0.28, knee 0.18, hip_yaw 0.06 |
| Dốc 10°, 15°, 18° | xoay trọng lực theo x, y, 45° | trượt ≤ 0.16 mm; mô-men ≤ 0.14 |
| Đẩy ngang 0.5·μ·m·g (14.46 N) | tăng dần trong 0.5 s, 24 hướng, giữ tổng 2 s | trượt lớn nhất 0.414 mm (hướng 135°), ngưỡng 0.5 mm |
| Bộ giải | `d.warning`, `solver_niter`, độ lún | không cảnh báo, ≤ 13/100 vòng lặp, lún ≤ 1.24 mm |

**Rủi ro cần chốt ở G1:**
- Đẩy **đột ngột** (lực bậc thang) theo hướng chéo 30–45° làm một bàn chân chạm giới hạn ma sát và trượt một lần khoảng 0.7 mm, sau đó đứng yên. Nếu cần chịu va đẩy đột ngột: hạ tải xuống thấp hơn hoặc mở rộng thế đứng.
- Biên mỏng: mô-men 3 chân 0.448/0.5, trượt 0.414/0.5 mm. Servo thật yếu hơn ước lượng thì có thể không qua.

## Sửa trong Blender (chỉ khi cần chỉnh hình học, 19.10)

Xem và kiểm model thì dùng MuJoCo (mục dưới). Blender chỉ mở khi cần sửa.

1. Mở `models/spider.blend` trong Blender 5.2.
2. Outliner → collection `robot` để thấy cây link: `torso` → `{leg}_coxa` → `{leg}_femur` → `{leg}_tibia` → Empty `{leg}_foot`.
3. Chọn một link → phím N → tab Item → Custom Properties để xem `joint`, `kind`, `axis`, `range_deg`, `servo`.

**Trước khi lưu:** nếu đã xoay thử link trong Blender, đưa về tư thế 0 (chọn các link trong `robot` → Alt+R) rồi mới lưu. Tư thế lúc lưu chính là góc 0 của mọi khớp, và không công cụ nào phát hiện được nếu lỡ lưu khi đang xoay.

Sau khi sửa và lưu trong Blender, kiểm lại bằng `tools/blender inspect`.

## Cách xem trong MuJoCo

```sh
tools/blender export                       # dựng lại build/model từ models/spider.blend
uv run python -m spider.sim.view           # mở viewer, tư thế stand
uv run python -m spider.sim.view --keyframe home
```

Trong viewer:
- Bảng trái → *Rendering* → *Label*: chọn *Joint* để hiện tên khớp.
- Bảng phải → *Control*: kéo thanh trượt để quay thử từng servo.

## Checklist cho người duyệt

- [ ] 4 chân xếp chữ X, đúng thứ tự `fl`, `fr`, `rl`, `rr` (trước-trái, trước-phải, sau-trái, sau-phải).
- [ ] Chiều quay đúng: `hip_pitch` dương nhấc đùi lên; `knee` dương gập cẳng xuống; `hip_yaw` quay quanh trục đứng.
- [ ] Tỉ lệ giống ảnh tham khảo, chỉ to hơn (19.2): thân 20 × 16 cm, chân duỗi khoảng 26 cm.
- [ ] Khối lượng không tải 1275.6 g và có tải 3275.6 g hợp lý.
- [ ] Hộp tải 2 kg đặt giữa mặt trên thân chấp nhận được, hoặc cần hạ thấp (rủi ro đẩy chéo đột ngột).
- [ ] Biên mô-men 3 chân 0.448/0.5 chấp nhận được với servo ước lượng.
- [ ] Ảnh Blender và ảnh MuJoCo `home` trùng nhau.
