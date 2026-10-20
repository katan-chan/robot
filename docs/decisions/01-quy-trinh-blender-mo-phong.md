# Bước 1. Quy trình Blender → mô phỏng

Ngày: 2026-10-20. Loại: tìm hiểu, chưa có quyết định.

## Người ta thường làm thế nào

1. Chọn simulator trước, vì nó quyết định định dạng file:
   - MuJoCo dùng MJCF/URDF.
   - Gazebo dùng URDF/SDF.
   - Isaac Sim nhận URDF/MJCF rồi chuyển sang USD.
2. Dựng trong Blender:
   - Mỗi link là một object riêng, origin đặt tại trục khớp.
   - Đơn vị là mét, hướng Z-up, apply scale trước khi export.
3. Làm hai bộ mesh:
   - Visual: chi tiết, dùng để hiển thị.
   - Collision: low-poly, dưới 1000 mặt mỗi link, hoặc dùng khối cơ bản.
4. Export mesh từng link ra STL, OBJ, DAE hoặc GLB.
5. Mô tả động học bằng URDF/MJCF: link, joint (loại, trục, giới hạn), khối lượng, inertia.
6. Kiểm tra bằng `check_urdf` (cần ROS urdfdom, chỉ dùng cho URDF) hoặc viewer, sau đó mới gắn bộ điều khiển. Với dự án này, MJCF được sinh trực tiếp, nên kiểm tra bằng `mujoco.MjModel.from_xml_path` cộng với script kiểm tra.

## Lỗi hay gặp

- Armature của Blender không trở thành khớp vật lý. Khớp phải khai báo trong URDF/MJCF.
- Sai đơn vị mm/m hoặc quên apply scale làm inertia sai, robot "nổ" hoặc rung.
- Chỉ khi **import URDF**, MuJoCo mới mặc định gộp các link nối bằng khớp fixed (`fusestatic`) và bỏ visual mesh (`discardvisual`). Với MJCF viết trực tiếp, cả hai mặc định là `false`, nên giữ nguyên mặc định. MJCF không có "khớp fixed", chỉ có body không có joint.

## Công cụ Blender

- Phobos (DFKI): xuất URDF/SDF. Viết cho Blender 3.x, có thể không chạy trên 5.x.
- LinkForge (extensions.blender.org): xuất URDF/XACRO, có linter.
- Cả hai đều là công cụ xuất URDF. Dự án này sinh MJCF từ Python, nên không cần chúng. Blender chỉ dùng để xuất mesh từng link (GLB/OBJ/STL).

## Nguồn

- https://forums.developer.nvidia.com/t/blender-to-isaac-sim/361514
- https://robotik.dfki-bremen.de/en/research/softwaretools/phobos
- https://extensions.blender.org/add-ons/linkforge/
- https://mirror.umd.edu/roswiki/urdf(2f)XML(2f)link.html
- https://docs.picknik.ai/how_to/configuration_tutorials/create_robot_sim_config/migrate_to_mujoco_config/
