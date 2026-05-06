# TÓM TẮT KẾT QUẢ LUẬN VĂN

**Đề tài:** Phương pháp xác minh chủ động dựa trên bản sao số với trọng số hiệu năng nhằm nâng cao tính chống chịu của Học liên kết trong phát hiện xâm nhập IoT

**Học viên:** Phạm Hoàng Hảo — MSHV: CH21210101005 — Khóa 16

**Cán bộ hướng dẫn:** TS. Phan Thế Duy, PGS. TS. Phạm Văn Hậu

---

## 7. Tóm tắt các kết quả của luận văn

Luận văn đề xuất **DT-Guard** — khung phòng thủ chủ động dùng **Digital Twin** làm "phòng thử nghiệm ảo" tại server cho Học liên kết (FL) trong phát hiện xâm nhập IoT. Mỗi mô hình client được chạy thử trên dữ liệu thách thức để đánh giá *hành vi suy luận thực tế* qua hai cơ chế: **Pipeline kiểm định 4 lớp** (Trust-Score) và **DT-PW + Effort Gate** (Performance-Score). Kết quả mới trên CIC-IoT-2023 và ToN-IoT (20 client, 5 loại tấn công Backdoor/LIE/Min-Max/Min-Sum/MPAF, tỉ lệ độc hại 10%–50%):

- **Detection Rate cao và ổn định**: 89,5%–98,3% (CIC-IoT-2023), 90%–100% (ToN-IoT) trước cả 5 loại tấn công, trong khi từng baseline (Krum, Median, GeoMed, SignGuard, ClipCluster, LUP, PoC,…) đều sụp đổ trước ít nhất một loại.
- **FPR = 0%** trên toàn bộ 40 kịch bản, không loại nhầm client Non-IID lành tính (LUP: 26,7%).
- **Loại 100% free-rider** nhờ DT-PW, trong khi Trust-Score thuần thưởng cho free-rider gấp 188 lần client thật.
- **Chi phí thấp**: 80,8 ms/vòng (< 1%), bộ nhớ đỉnh 485 MB.

---

## 8. Khả năng ứng dụng thực tiễn

- **Hệ thống FL-IDS cho IoT/IIoT** (smart home, smart factory, smart city, mạng cảm biến công nghiệp): tích hợp DT-Guard vào server tổng hợp để loại bỏ client độc hại và free-rider mà không cần truy cập dữ liệu thô của thiết bị, đảm bảo quyền riêng tư.
- **Module aggregator thay thế FedAvg** trong các nền tảng FL phổ biến (Flower, FATE, NVIDIA FLARE): bổ sung lớp kiểm chứng hành vi cho các hệ thống FL hiện hữu nhằm tăng khả năng chống chịu poisoning/backdoor và bảo đảm công bằng đóng góp giữa các bên tham gia.
- **Chia sẻ tri thức an toàn liên tổ chức** (liên ngân hàng, liên bệnh viện, liên nhà mạng): cơ chế DT-PW định lượng đóng góp tri thức thực tế thay vì chỉ dựa trên số lượng mẫu khai báo, giúp các tổ chức được tưởng thưởng tương xứng và hạn chế hành vi free-riding.

---

## 9. Những hướng nghiên cứu tiếp theo

- **Mở rộng quy mô lên hàng nghìn client**: chạy nhiều Digital Twin instance song song trên GPU cluster, lấy mẫu (sampling) chỉ kiểm chứng một tỉ lệ client mỗi vòng và mở rộng sang kiến trúc phân cấp edge → fog → cloud để giảm tải tính toán tập trung.
- **Triển khai và đánh giá trên testbed IoT thực tế** (Raspberry Pi, ESP32, gateway công nghiệp): kiểm chứng tính khả thi trong điều kiện độ trễ mạng, mất gói, client dropout và sự không đồng nhất về tài nguyên — những yếu tố chưa xuất hiện trong môi trường mô phỏng.
- **Đánh giá trước tấn công thích nghi (adaptive attacks)** và mở rộng sang **FL bất đồng bộ (Asynchronous FL)**: thiết kế các tấn công được tối ưu riêng để vượt qua Trust Gate và Effort Gate; điều chỉnh hai cổng này cho nhịp cập nhật không đồng đều giữa các client.
- **Tích hợp Blockchain** cho audit log bất biến: ghi nhận Trust-Score, Performance-Score và quyết định verification lên chain để đảm bảo tính minh bạch, không thể chối cãi và có thể kiểm toán bởi bên thứ ba.

---

## 10. Các công trình đã công bố có liên quan đến luận văn

1. **Phạm Hoàng Hảo, Phan Thế Duy, Phạm Văn Hậu** (2026), *"Active Digital Twin Verification for Robust Federated Learning in IoT Intrusion Detection"*, Proc. 2026 Eleventh International Conference on Communications and Electronics (ICCE 2026) — Communication Networks and Systems, IEEE, Nha Trang, Việt Nam. *(Đã đệ trình, đang chờ phản biện.)*





