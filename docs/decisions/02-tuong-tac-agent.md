# Bước 2. Simulator tương tác với agent

Ngày: 2026-10-20. Loại: tìm hiểu, chưa có quyết định.

## Ba kiểu tương tác

1. **RL agent**: dùng vòng lặp Gymnasium.
   ```
   obs, info = env.reset()
   loop:
       action = policy(obs)
       obs, reward, terminated, truncated, info = env.step(action)
   ```
   Tần số 50–1000 Hz, train bằng PPO/SAC qua hàng triệu bước.
2. **LLM agent**: gọi tool qua MCP, ví dụ set góc khớp, đọc trạng thái, step, render.
   - LLM mất cỡ vài giây mỗi quyết định, nên chỉ ra lệnh cấp cao.
   - Bộ điều khiển cấp thấp (PD, IK) chạy liên tục bên trong sim.
3. **ROS 2**: MCP server chạy như một ROS node, publish/subscribe topic (ví dụ `/cmd_vel`). Trên macOS cài khó.

## Hệ quả cho model robot

- Joint phải có tên rõ ràng.
- Mỗi joint có actuator kèm giới hạn lực và góc.
- Có cảm biến: encoder khớp, IMU, camera khi cần.
- Collision đơn giản để sim chạy nhanh.

## Nguồn

- https://gymnasium.farama.org/v1.1.1/introduction/basic_usage/
- https://uniros.readthedocs.io/en/latest/guides/env_creation_sim_mujoco.html
- https://glama.ai/mcp/servers/yoq665ijxs
- https://glama.ai/mcp/servers/Rongxuan-Zhou/mujoco-mcp-server
- https://glama.ai/mcp/servers/kakimochi/ros2-mcp-server
