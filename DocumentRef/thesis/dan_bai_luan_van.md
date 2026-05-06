# DÀN BÀI LUẬN VĂN THẠC SỸ
# Đề tài: Phương pháp xác minh chủ động dựa trên bản sao số với trọng số hiệu năng cao tính chống chịu của học liên kết trong phát hiện xâm nhập IoT

---

## LƯU Ý KHI VIẾT NỘI DUNG:

### 1. Hình kiến trúc (Architecture Diagrams)
- **KHÔNG tự vẽ hình** - chừa lại placeholder để vẽ bằng file `.tex` sau
- Ví dụ format: `[Hình 3.1] Kiến trúc tổng thể DT-Guard (xem file tex)`
- Các vị trí cần vẽ:
  - Chương 1.1.1: Kiến trúc IoT 3 lớp
  - Chương 1.5.1: Vòng đời Digital Twin
  - Chương 3.2.1: Kiến trúc ba thực thể DT-Guard
  - Chương 3.2.3: Luồng hoạt động 5 bước
  - Chương 3.4: Pipeline kiểm định 4 lớp
  - Chương 3.5: Cơ chế DT-PW với Effort Gate

### 2. Hình kết quả thực nghiệm (Result Figures)
- **Chỉ cần để đường dẫn** đến thư mục kết quả, tự điền sau
- Đường dẫn kết quả: `/Users/hao.pham/PycharmProjects/DTGuardFL/DT-Guard-FL/results`
- Ví dụ format: `[Hình 4.1] Accuracy trên CIC-IoT-2023 (results/paper/accuracy_plot.png)`
- Các vị trí cần hình kết quả:
  - Chương 4.2.1: Accuracy/DR/FPR trên CIC-IoT-2023 theo từng tấn công và tỷ lệ
  - Chương 4.2.2: Accuracy/DR/FPR trên ToN-IoT theo từng tấn công và tỷ lệ
  - Chương 4.2.3: So sánh chéo giữa hai dataset
  - Chương 4.3: Kết quả A/B Testing mô hình sinh
  - Chương 4.4: Trọng số cho free-rider vs client thường

---

## PHẦN MỞ ĐẦU

### 1. Lý do chọn đề tài
- Bối cảnh: IoT phát triển mạnh (số lượng thiết bị tăng nhanh), ứng dụng trong các lĩnh vực quan trọng
- Vấn đề an toàn thông tin: Các cuộc tấn công ngày càng tinh vi
- Hệ thống IDS truyền thống: Cần tập trung hóa dữ liệu → xung đột với quyền riêng tư
- FL xuất hiện như giải pháp nhưng đối mặt với thách thức bảo mật mới
- Cần phương pháp phòng thủ vượt trội hơn các phương pháp hiện có

### 2. Tính cấp thiết của đề tài
- Các phương pháp phòng thủ hiện tại đều thất bại trước ít nhất một loại tấn công
- Vấn đề FPR cao do nhầm lẫn giữa Non-IID và hành vi đầu độc
- Vấn đề free-rider chưa được giải quyết thấu đáo
- Nhu cầu chuyển từ phân tích tham số thụ động sang kiểm chứng hành vi chủ động

### 3. Mục tiêu nghiên cứu
- (i) Xây dựng khung DT-Guard tích hợp Digital Twin làm môi trường kiểm chứng hành vi chủ động
- (ii) Thiết kế cơ chế DT-PW để định lượng đóng góp tri thức thực tế và phát hiện free-rider
- (iii) Đánh giá toàn diện trên bộ dữ liệu CIC-IoT-2023 và so sánh với các phương pháp phòng thủ đại diện

### 4. Đối tượng và phạm vi nghiên cứu
- Đối tượng: Cơ chế phòng thủ chủ động cho FL trong IoT IDS
- Phạm vi dữ liệu: CIC-IoT-2023, ToN-IoT
- Phạm vi mô hình: IoTAttackNet, XGBoost
- Phạm vi tấn công: Backdoor, LIE, Min-Max, Min-Sum, MPAF
- Phạm vi tỷ lệ tấn công: 4 mức (10%, 20%, 40%, 50%) đánh giá từ nhẹ đến khắc nghiệt
- Phạm vi phòng thủ đối sánh: FedAvg, Krum, Median, Trimmed Mean, GeoMed, SignGuard, ClipCluster, LUP, PoC

### 5. Đóng góp của đề tài
- Đóng góp 1: Khung DT-Guard với pipeline kiểm định hành vi 4 lớp
- Đóng góp 2: Cơ chế DT-PW với Effort Gate phát hiện free-rider
- Đóng góp 3: Bộ sinh dữ liệu thách thức dựa trên TabDDPM
- Đóng góp 4: Đánh giá trên hai dataset chứng minh khả năng tổng quát hóa
- Đóng góp 5: Phân tích overhead và trade-off chi phí - lợi ích

### 6. Ý nghĩa khoa học và thực tiễn
- Ý nghĩa khoa học: Paradigm mới active behavioral verification, chứng minh cross-dataset generalization, giải quyết đồng thời ba vấn đề
- Ý nghĩa thực tiễn: Framework triển khai được, giải quyết bài toán công bằng, hướng dẫn chọn mô hình sinh dữ liệu

### 7. Cấu trúc luận văn
- Giới thiệu ngắn gọn 5 chương chính

---

## CHƯƠNG 1. TỔNG QUAN VỀ VẤN ĐỀ NGHIÊN CỨU

### 1.1. Giới thiệu về Internet of Things (IoT)
#### 1.1.1. Khái niệm và kiến trúc IoT
- Định nghĩa IoT
- Kiến trúc IoT 3 lớp (Perception, Network, Application)
- Các thiết bị và giao thức IoT phổ biến
> **NOTE: [Hình 1.1] Kiến trúc IoT 3 lớp - chừa placeholder cho file .tex**

#### 1.1.2. Thách thức an toàn thông tin trong IoT
- Đặc tính của IoT: thiết bị nhiều, phân tán, tài nguyên hạn chế
- Các mối đe dọa an toàn thông tin trong IoT
- Yêu cầu bảo vệ quyền riêng tư dữ liệu

### 1.2. Hệ thống phát hiện xâm nhập mạng (Intrusion Detection System)
#### 1.2.1. Khái niệm và nguyên lý hoạt động của IDS
- Định nghĩa IDS
- Quy trình hoạt động cơ bản
- Vai trò của IDS trong hệ thống an toàn thông tin

#### 1.2.2. Phân loại IDS
- Theo phương pháp phát hiện: Signature-based, Anomaly-based, Hybrid
- Theo vị trí triển khai: Network-based (NIDS), Host-based (HIDS)

#### 1.2.3. Hạn chế của IDS truyền thống trong ngữ cảnh IoT
- Cần tập trung hóa dữ liệu
- Vấn đề băng thông và độ trễ
- Xung đột với quy định quyền riêng tư
- FL xuất hiện như giải pháp thay thế

### 1.3. Tổng quan về Học liên kết (Federated Learning)
#### 1.3.1. Khái niệm và nguyên lý FL
- Định nghĩa FL
- Quy trình hoạt động cơ bản: Local training → Upload → Aggregate → Broadcast
- FedAvg: Thuật toán tổng hợp mặc định

#### 1.3.2. FL trong ngữ cảnh IoT IDS
- Lợi ích: Bảo vệ quyền riêng tư, tiết kiệm băng thông, tận dụng dữ liệu phân tán
- Thách thức đặc thù:
  - Dữ liệu Non-IID (label skew, quantity skew, feature skew)
  - Mất cân bằng lớp
  - Thiết bị không đồng nhất (system heterogeneity)
  - Các vấn đề bảo mật

#### 1.3.3. Các bộ dữ liệu chuẩn cho IoT IDS
- Nhu cầu benchmark dataset
- Tổng hợp các dataset IoT IDS phổ biến (NSL-KDD, KDD CUP 99, UNSW-NB15)
- CIC-IoT-2023: Đặc điểm, quy mô, các lớp tấn công
- ToN-IoT: Đặc điểm, cấu trúc

### 1.4. Các hình thức tấn công trong Federated Learning
#### 1.4.1. Phân loại tấn công trong FL
- Theo mục tiêu: Untargeted vs Targeted
- Theo loại dữ liệu: Data poisoning vs Model poisoning
- Các mối đe dọa: Poisoning, Byzantine, Free-riding, Inference attacks

#### 1.4.2. Các dạng tấn công poisoning và backdoor
- LIE (A Little Is Enough): Cơ chế, đặc điểm [ref: Baruch 2019]
- Min-Max và Min-Sum: Cơ chế, đặc điểm [ref: Shejwalkar 2021]
- MPAF (Model Poisoning Attacks based on Fake clients): Cơ chế, đặc điểm
- Backdoor Attack: Cơ chế, đặc điểm, khác biệt với untargeted attacks

### 1.5. Các phương pháp phòng thủ hiện có cho Federated Learning
#### 1.5.1. Nhóm thống kê cổ điển
- Krum: Nguyên lý chọn update [ref: Blanchard 2017]
- Coordinate-wise Median: Nguyên lý lấy trung vị [ref: Yin 2018]
- Trimmed Mean: Nguyên lý cắt và lấy trung bình [ref: Yin 2018]
- GeoMed: Nguyên lý geometric median [ref: Pillutla 2022]

#### 1.5.2. Nhóm phân tích nâng cao
- SignGuard: Phân tích hướng dấu gradient [ref: Xu 2022]
- ClipCluster: Norm clipping và cosine clustering [ref: Zeng 2024]
- LUP: MAD, hierarchical clustering, Trust Score [ref: Issa 2025]
- PoC: Proof of Contribution dựa trên MMD [ref: Zhang 2025]

#### 1.5.3. Phương pháp dựa trên Shapley Value
- Shapley Value: Khái niệm cơ bản [ref: Shapley 1953]
- Ứng dụng trong FL cho định lượng đóng góp [ref: Zhang 2025]

### 1.6. Digital Twin và ứng dụng trong FL-IoT
#### 1.6.1. Khái niệm Digital Twin
- Định nghĩa DT
- Vòng đời DT: Tạo → Kết nối → Mô phỏng → Phân tích → Tối ưu hóa
- Ứng dụng DT trong IoT: simulation, optimization, anomaly detection, testing
> **NOTE: [Hình 1.2] Vòng đời Digital Twin - chừa placeholder cho file .tex**

#### 1.6.2. Các nghiên cứu DT-FL gần đây
- DT-BFL: Digital Twins cho Blockchain-enabled FL [ref: Issa 2025]
- BAFL-DT: DT-based Adaptive FL cho fog computing [ref: Qu 2021]
- PPSG: Adaptive Asynchronous FL với DT cho Smart Grid [ref: Zhang 2025]
- DITEN: DT-enhanced Incremental Transfer Learning [ref: Lu 2020]

#### 1.6.3. Tổng hợp và nhận diện khoảng trống
- Các nghiên cứu DT-FL hiện tại dùng DT cho infrastructure/resource management
- Không có nghiên cứu dùng DT làm behavioral testing sandbox
- Các phương pháp phòng thủ đều thực hiện passive parameter inspection
- Vấn đề: LIE/Min-Max/Min-Sum qua mặt được; FPR cao do nhầm Non-IID; Free-rider được thưởng

### 1.7. Tổng kết chương
- Tóm tắt các nội dung chính
- Xác định 3 khoảng trống nghiên cứu dẫn vào Chương 2

---

## CHƯƠNG 2. CƠ SỞ LÝ THUYẾT VÀ CÔNG NGHỆ NỀN TẢNG

### 2.1. Cơ sở lý thuyết Federated Learning
#### 2.1.1. Bài toán tối ưu phân tán trong FL
- Công thức tối ưu hóa FL
- Hàm mất mát tổng thể
- Thách thức trong môi trường phân tán

#### 2.1.2. Thuật toán FedAvg
- Quy trình chi tiết
- Cách tính trọng số client
- Phân tích hội tụ

#### 2.1.3. Dữ liệu Non-IID trong FL
- Định nghĩa Non-IID
- Phân tích mức độ Non-IID theo Dirichlet
- Ảnh hưởng đến hội tụ và hiệu năng

#### 2.1.4. Weighted Cross-Entropy Loss cho mất cân bằng lớp
- Vấn đề mất cân bằng lớp trong IDS
- Cross-Entropy Loss truyền thống
- Weighted Cross-Entropy: Công thức và cơ chế

### 2.2. Cơ sở lý thuyết các tấn công poisoning và backdoor
#### 2.2.1. Tấn công LIE (A Little Is Enough)
- Phân tích chi tiết cơ chế
- Công thức toán học
- Tại sao qua mặt được các phương pháp dựa trên khoảng cách

#### 2.2.2. Tấn công Min-Max và Min-Sum
- Bài toán tối ưu hóa của Min-Max
- Bài toán tối ưu hóa của Min-Sum
- Phương pháp giải (binary search)
- Ràng buộc khoảng cách và ảnh hưởng lên Krum, GeoMed

#### 2.2.3. Tấn công MPAF
- Cơ chế tạo fake clients
- Phá vỡ giả định honest majority
- Ảnh hưởng lên các phương pháp dựa trên clustering

#### 2.2.4. Tấn công Backdoor
- Cơ chế chèn trigger
- Mapping trigger → target class
- Tại sao khó phát hiện với passive methods

#### 2.2.5. Free-rider problem
- Định nghĩa free-rider
- Tại sao các phương pháp dựa trên khoảng cách tham số thưởng cho free-rider
- Vấn đề công bằng trong FL

### 2.3. Cơ sở lý thuyết Digital Twin
#### 2.3.1. Mô hình khái niệm Digital Twin
- Thành phần: Physical Entity, Digital Model, Data Connection, Services
- Vòng đời DT trong FL: Deploy → Verify → Update → Deploy

#### 2.3.2. Server-side DT cho behavioral testing
- Sandbox isolation: Tách biệt từ FL Server chính
- Parallel verification: Kiểm chứng song song nhiều clients
- Challenge generation: Dữ liệu kiểm thử được kiểm soát

#### 2.3.3. Kiểm chứng hành vi chủ động vs Phân tích tham số thụ động
- So sánh hai paradigm
- Ưu nhược điểm của mỗi phương pháp
- Tại sao active behavioral verification vượt trội

### 2.4. Cơ sở lý thuyết mô hình sinh dữ liệu dạng bảng
#### 2.4.1. Denoising Diffusion Probabilistic Models (DDPM)
- Nguyên lý diffusion process
- Forward process: Thêm nhiễu dần
- Reverse process: Khử nhiễu dần
- Training objective

#### 2.4.2. TabDDPM cho dữ liệu bảng
- Điểm khác biệt với DDPM gốc
- Xử lý biến phân loại và liên tục
- Ưu điểm: Fidelity cao, stability tốt

#### 2.4.3. Các mô hình đối sánh
- CTGAN: Conditional GAN cho tabular data [ref: Xu 2019]
- WGAN-GP: Wasserstein GAN with Gradient Penalty
- So sánh: Diffusion vs GAN

### 2.5. Cơ sở lý thuyết mô hình Intrusion Detection
#### 2.5.1. Kiến trúc IoTAttackNet
- Multilayer Perceptron (MLP)
- Kiến trúc: Input → Hidden layers → Output
- Activation functions: ReLU, Softmax
- Thích hợp cho dữ liệu high-dimensional

#### 2.5.2. XGBoost
- Gradient Boosted Decision Trees
- Ưu điểm cho dữ liệu tabular compact
- Thích hợp cho ToN-IoT dataset

#### 2.5.3. Các chỉ số đánh giá
- Accuracy, Precision, Recall, F1-Score
- Detection Rate (DR)
- False Positive Rate (FPR)

### 2.6. Cơ sở lý thuyết bộ dữ liệu thực nghiệm
#### 2.6.1. CIC-IoT-2023
- Nguồn và cấu trúc
- Thống kê: số flows, đặc trưng, lớp
- Các danh mục tấn công
- Lý do lựa chọn cho đề tài

#### 2.6.2. ToN-IoT
- Nguồn và cấu trúc
- Thống kê: số mẫu, đặc trưng, lớp
- Lý do cần thêm dataset thứ hai (generalization)

### 2.7. Tổng kết chương
- Tóm tắt các lý thuyết nền tảng
- Chuẩn bị cho Chương 3

---

## CHƯƠNG 3. ĐỀ XUẤT HỆ THỐNG DT-GUARD

### 3.1. Phát biểu bài toán và ý tưởng cốt lõi
#### 3.1.1. Phát biểu bài toán phòng thủ trong FL-IDS
- Input: N clients, K malicious clients, local models
- Output: Global model robust, rejected malicious clients, fair weights
- Ràng buộc: Không truy cập dữ liệu thô, overhead thấp

#### 3.1.2. Ý tưởng cốt lõi: Behavioral Testing
- Chuyển từ passive parameter inspection → active behavioral verification
- Server-side DT như sandbox để kiểm chứng hành vi
- Kiểm chứng trên challenge data được kiểm soát

### 3.2. Kiến trúc tổng thể DT-Guard
#### 3.2.1. Kiến trúc ba thực thể
- IoT Clients: Huấn luyện cục bộ, gửi update
- FL Server: Tổng hợp model, điều phối quá trình
- DT Verification Environment: Sandbox tách biệt, kiểm chứng hành vi
> **NOTE: [Hình 3.1] Kiến trúc ba thực thể DT-Guard - chừa placeholder cho file .tex**

#### 3.2.2. Các thành phần chính
- Challenge Data Generator: Bộ sinh dữ liệu thách thức
- Digital Twin Sandbox: Môi trường kiểm chứng
- Trust Gate: Pipeline kiểm định 4 lớp
- DT-PW Scorer: Đánh giá đóng góp tri thức
- Aggregator: Tổng hợp weighted aggregation

#### 3.2.3. Luồng hoạt động 5 bước
- Bước 1: Upload - Client gửi update về FL Server
- Bước 2: Deploy - Server triển khai vào DT Sandbox
- Bước 3: Gate & Aggregate - Hai cơ chế kiểm chứng quyết định chấp nhận/loại bỏ
- Bước 4: Update - Tổng hợp model mới
- Bước 5: Broadcast - Phân phối lại cho clients
> **NOTE: [Hình 3.2] Luồng hoạt động 5 bước DT-Guard - chừa placeholder cho file .tex**

#### 3.2.2. Các thành phần chính
- Challenge Data Generator: Bộ sinh dữ liệu thách thức
- Digital Twin Sandbox: Môi trường kiểm chứng
- Trust Gate: Pipeline kiểm định 4 lớp
- DT-PW Scorer: Đánh giá đóng góp tri thức
- Aggregator: Tổng hợp weighted aggregation

#### 3.2.3. Luồng hoạt động 5 bước
- Bước 1: Upload - Client gửi update về FL Server
- Bước 2: Deploy - Server triển khai vào DT Sandbox
- Bước 3: Gate & Aggregate - Hai cơ chế kiểm chứng quyết định chấp nhận/loại bỏ
- Bước 4: Update - Tổng hợp model mới
- Bước 5: Broadcast - Phân phối lại cho clients

### 3.3. Bộ sinh dữ liệu thách thức
#### 3.3.1. Yêu cầu đối với challenge data
- Fidelity: Phản ánh phân phối thực
- Coverage: Bao phủ đa dạng các lớp
- Diversity: Mẫu đa dạng, không trùng lặp
- Efficiency: Tốc độ sinh nhanh

#### 3.3.2. A/B Testing chọn mô hình sinh
- Các mô hình được đánh giá: TabDDPM, TabSyn, ForestDiffusion, CTGAN, WGAN-GP
- Tiêu chí đánh giá: TSTR, Wasserstein Distance, DCR, Recall, Training Time, Latency
- Kết quả: TabDDPM được chọn với composite score cao nhất

#### 3.3.3. Quy trình sinh dữ liệu thách thức
- Huấn luyện TabDDPM trên benign data
- Pre-generate challenge pool để giảm latency
- Lấy mẫu có điều kiện (conditional sampling) cho các lớp cụ thể

### 3.4. Pipeline kiểm định hành vi với Trust-Score
> **NOTE: [Hình 3.3] Pipeline kiểm định hành vi 4 lớp với Trust-Score - chừa placeholder cho file .tex**
#### 3.4.1. Lớp 1: IDS Performance Score
- Đánh giá hiệu năng phát hiện xâm nhập trên challenge data
- Metric: F1-Score
- Công thức: S_perf = F1(model, X_challenge, y_challenge)

#### 3.4.2. Lớp 2: Backdoor Resistance Score
- Phát hiện qua độ lệch chuẩn bất thường của softmax confidence
- Confidence distribution: Benign samples có confidence ổn định, backdoor có confidence bất thường
- Công thức: S_br = 1 - (σ(conf) - μ_benign) / σ_benign

#### 3.4.3. Lớp 3: Parameter Deviation Score
- Đánh giá mức lệch tham số so với mô hình toàn cục
- Metric: L2 distance, cosine distance
- Công thức: S_param = 1 - ||w_local - w_global||_2 / max_k ||w_k - w_global||_2

#### 3.4.4. Lớp 4: Cross-Round Stability Score
- Đánh giá độ ổn định qua các vòng
- Phát hiện attacker thay đổi chiến thuật liên tục
- Công thức: S_stab = 1 - Var(S_perf^history)

#### 3.4.5. Trust-Score Fusion
- Cơ chế thích ứng: Balanced mode vs Strict mode
- Balanced mode (khi parameter deviation thấp): T = 0.7 × S_perf + 0.3 × S_param
- Strict mode (khi parameter deviation cao): T = min(S_perf, S_param)
- Ngưỡng chấp nhận: Client được chấp nhận nếu T ≥ θ_T

### 3.5. Cơ chế DT-PW với Effort Gate
> **NOTE: [Hình 3.4] Cơ chế DT-PW với Effort Gate - chừa placeholder cho file .tex**
#### 3.5.1. Prediction Divergence
- Đánh giá mức khác biệt dự đoán giữa client và global model
- Client thực sự huấn luyện: divergence cao
- Free-rider: divergence thấp (dự đoán gần như y hệt)
- Công thức: d_i = (1/|X|) × Σ_x∈X 1[ŷ_local(x) ≠ ŷ_global(x)]

#### 3.5.2. Effort Gate
- Ngưỡng thích ứng: θ_E = μ_d - β × σ_d
- Cơ chế:
  - Nếu d_i < θ_E: Free-rider → P_i = 0
  - Nếu d_i ≥ θ_E: Client thực sự → P_i = s_i^ids × d_i / max_k d_k

#### 3.5.3. Trọng số tổng hợp cuối cùng
- Công thức: w_i = (T_i × P_i) / Σ_j (T_j × P_j)
- Đảm bảo: chỉ client vừa đáng tin (T cao) vừa đóng góp (P cao) mới có trọng số lớn

### 3.6. Phân tích lý thuyết
#### 3.6.1. Tại sao behavioral testing vượt trội passive analysis
- Tham số không phản ánh trực tiếp hành vi suy luận
- LIE/Min-Max/Min-Sum giữ tham số trong vùng thống kê nhưng hành vi sai
- Client Non-IID có tham số lệch nhưng hành vi đúng
- DT verification phát hiện qua hành vi thực sự

#### 3.6.2. Đảm bảo an toàn với sandbox isolation
- DT Sandbox tách biệt từ FL Server chính
- Hành vi độc hại không ảnh hưởng trực tiếp
- Có thể reset sandbox sau mỗi verification

#### 3.6.3. Độ phức tạp tính toán
- Chi phí verification: O(C × N) với C là số challenge samples, N là số clients
- Chi phí DT-PW: O(C × N)
- Tổng overhead: Tối ưu hóa với pre-generated challenge pool

### 3.7. Tổng kết chương
- Tóm tắt kiến trúc DT-Guard
- Các thành phần chính và vai trò

---

## CHƯƠNG 4. THỰC NGHIỆM VÀ ĐÁNH GIÁ

### 4.1. Thiết lập thực nghiệm
#### 4.1.1. Môi trường thực nghiệm
- Hardware: CPU, RAM, GPU
- Software: Python, PyTorch, các thư viện

#### 4.1.2. Cấu hình Federated Learning
- Số clients: 20
- Số rounds: 20
- Local epochs: 3
- Batch size: 512
- Phân bổ dữ liệu: Dirichlet α = 0.5
- Tỷ lệ client độc hại: 4 mức đánh giá (10%, 20%, 40%, 50%), tương ứng 2, 4, 8, 10 clients trong 20

#### 4.1.3. Các phương pháp đối sánh
- Nhóm không phòng thủ: FedAvg
- Nhóm thống kê cổ điển: Krum, Median, Trimmed Mean, GeoMed
- Nhóm phân tích nâng cao: SignGuard, ClipCluster, LUP, PoC
- Đề xuất: DT-Guard

#### 4.1.4. Các chỉ số đánh giá
- Accuracy: Hiệu năng IDS toàn cục
- Detection Rate: Tỷ lệ phát hiện client độc hại
- False Positive Rate: Tỷ lệ loại nhầm client lành tính

#### 4.1.5. Ma trận kịch bản thực nghiệm
- Kịch bản A: Đánh giá hiệu năng phòng thủ
  - 5 loại tấn công: Backdoor, LIE, Min-Max, Min-Sum, MPAF
  - 4 mức tỷ lệ client độc hại: 10%, 20%, 40%, 50%
  - Tổng cộng: 5 × 4 = 20 kịch bản
- Kịch bản B: Đánh giá bộ sinh dữ liệu thách thức (A/B Testing 5 mô hình)
- Kịch bản C: Đánh giá tính công bằng và phát hiện free-rider

### 4.2. Kịch bản A: Đánh giá hiệu năng phòng thủ
#### 4.2.1. Kết quả trên CIC-IoT-2023
- Đánh giá trên 4 mức tỷ lệ client độc hại: 10%, 20%, 40%, 50%
- Accuracy theo từng tấn công và từng tỷ lệ malicious
- Detection Rate theo từng tấn công và từng tỷ lệ malicious
- False Positive Rate theo từng tấn công và từng tỷ lệ malicious
- Phân tích xu hướng: Tại sao DT-Guard ổn định theo các mức độ tấn công?
> **NOTE: [Hình 4.1] Accuracy trên CIC-IoT-2023 theo tấn công và tỷ lệ - results/paper/accuracy_cic.png**
> **NOTE: [Hình 4.2] Detection Rate trên CIC-IoT-2023 theo tấn công và tỷ lệ - results/paper/dr_cic.png**
> **NOTE: [Hình 4.3] FPR trên CIC-IoT-2023 theo tấn công và tỷ lệ - results/paper/fpr_cic.png**

#### 4.2.2. Kết quả trên ToN-IoT
- Đánh giá trên 4 mức tỷ lệ client độc hại: 10%, 20%, 40%, 50%
- Accuracy theo từng tấn công và từng tỷ lệ malicious
- Detection Rate theo từng tấn công và từng tỷ lệ malicious
- False Positive Rate theo từng tấn công và từng tỷ lệ malicious
> **NOTE: [Hình 4.4] Accuracy trên ToN-IoT theo tấn công và tỷ lệ - results/paper/accuracy_ton.png**
> **NOTE: [Hình 4.5] Detection Rate trên ToN-IoT theo tấn công và tỷ lệ - results/paper/dr_ton.png**
> **NOTE: [Hình 4.6] FPR trên ToN-IoT theo tấn công và tỷ lệ - results/paper/fpr_ton.png**

#### 4.2.3. So sánh chéo giữa hai dataset
- Đánh giá trên cùng 4 mức tỷ lệ malicious (10%, 20%, 40%, 50%) cho cả hai dataset
- Tại sao cùng loại tấn công sụp đổ ở cả hai dataset?
- Cross-dataset generalization của DT-Guard
- Phân tích: Lỗ hổng cấu trúc của passive methods
> **NOTE: [Hình 4.7] So sánh chéo Accuracy giữa CIC-IoT-2023 và ToN-IoT - results/paper/cross_dataset_comparison.png**

#### 4.2.4. Giải thích hiện tượng Detection Rate thấp nhưng Accuracy vẫn cao
- Tại sao xảy ra hiện tượng này?
- Phân tích chi tiết

### 4.3. Kịch bản B: Đánh giá bộ sinh dữ liệu thách thức
#### 4.3.1. Kết quả A/B Testing
- TabDDPM vs TabSyn vs ForestDiffusion vs CTGAN vs WGAN-GP
- Chỉ số: TSTR, Wasserstein, DCR, Recall, Training Time, Latency
- Composite score: TabDDPM đạt cao nhất
> **NOTE: [Hình 4.8] Kết quả A/B Testing mô hình sinh dữ liệu - results/paper/ablation_generator.png**

#### 4.3.2. Lý do TabDDPM được chọn
- Cân bằng giữa fidelity, coverage, diversity, efficiency
- TSTR 71,4% (cao nhất), Wasserstein 0,061 (thấp nhất)
- Training time 200s (nhanh gấp 8× CTGAN)

### 4.4. Kịch bản C: Đánh giá tính công bằng và phát hiện free-rider
#### 4.4.1. Thiết lập kịch bản free-rider
- Số free-rider: 4 trong 20 clients
- Hành vi free-rider: Copy global model, add small noise

#### 4.4.2. Kết quả so sánh các chiến lược aggregation
- DT-PW vs Shapley Value vs Trust-Score vs Uniform
- Trọng số cho free-rider vs client thường
- Accuracy đạt được
> **NOTE: [Hình 4.9] Trọng số cho free-rider vs client thường theo từng chiến lược - results/paper/freerider_weights.png**

#### 4.4.3. Phân tích
- DT-PW phát hiện 100% free-rider (trọng số = 0)
- Trust-Score vô tình thưởng cho free-rider (0,2406 vs 0,0023)
- Hiện tượng "đảo ngược ý nghĩa"

### 4.5. Phân tích overhead và chi phí tài nguyên
#### 4.5.1. Thời gian thực thi
- Thời gian DT verification mỗi round
- Thời gian DT-PW scoring mỗi round
- Tổng overhead: ~0,08s/round (< 1%)
> **NOTE: [Hình 4.10] Thời gian thực thi theo từng phương pháp - results/paper/overhead_time.png**

#### 4.5.2. Bộ nhớ
- Peak Memory của DT-Guard
- So sánh với các baseline: 485MB vs 673MB (FedAvg)
> **NOTE: [Hình 4.11] Peak Memory theo từng phương pháp - results/paper/overhead_memory.png**

#### 4.5.3. Trade-off chi phí - lợi ích
- Chi phí tăng: ~0,08s/round, ~188MB memory
- Lợi ích thu được: FPR = 0% (thay vì 64,4% LUP), DR = 89,5%-100%

### 4.6. Bàn luận tổng hợp
#### 4.6.1. Tại sao DT-Guard hiệu quả?
- Chuyển từ passive → active behavioral verification
- Kiểm chứng trên challenge data được kiểm soát
- Pipeline 4 lớp đánh giá toàn diện

#### 4.6.2. Tại sao FPR = 0%?
- Client Non-IID dù tham số lệch nhưng hành vi đúng
- DT verification phát hiện qua hành vi thực sự
- Passive methods nhầm lẫn vì chỉ nhìn tham số

#### 4.6.3. Khả năng tổng quát hóa cross-dataset
- DT-Guard ổn định trên cả CIC-IoT-2023 và ToN-IoT
- Baseline sụp đổ trước cùng loại tấn công ở cả hai dataset
- Lỗ hổng của passive methods là cấu trúc, không phụ thuộc dataset

#### 4.6.4. So sánh trực tiếp với LUP
- LUP: Passive parameter inspection, FPR cao, thưởng free-rider
- DT-Guard: Active behavioral verification, FPR = 0%, phát hiện free-rider

#### 4.6.5. Các hạn chế nhận diện được
- Overhead tăng tuyến tính theo số client
- Phụ thuộc chất lượng bộ sinh TabDDPM
- Chưa thử nghiệm trên mạng IoT thực tế quy mô lớn

### 4.7. Tổng kết chương
- Tóm tắt các kết quả thực nghiệm
- Xác nhận các đóng góp của đề tài

---

## CHƯƠNG 5. KẾT LUẬN VÀ KHUYẾN NGHỊ

### 5.1. Tổng kết kết quả nghiên cứu
#### 5.1.1. Khung DT-Guard với pipeline kiểm định hành vi 4 lớp
- Thành công xây dựng kiến trúc thống nhất
- Giải quyết cả ba khoảng trống nghiên cứu

#### 5.1.2. Kết quả trên bộ dữ liệu CIC-IoT-2023
- Accuracy ổn định: 72,3% - 73,3%
- Detection Rate cao: 89,5% - 98,3%
- FPR = 0%

#### 5.1.3. Kết quả trên bộ dữ liệu ToN-IoT
- Accuracy ổn định: 99,8%
- Detection Rate cao: 96,0% - 100%
- FPR = 0%

#### 5.1.4. Kết quả overhead
- Thời gian: ~0,08s/round (< 1%)
- Bộ nhớ: 485MB (thấp nhất)
- Trade-off: Chi phí nhỏ, lợi ích lớn

### 5.2. Các đóng góp khoa học
#### 5.2.1. Paradigm mới: Active Behavioral Verification
- Thay thế Passive Parameter Inspection
- DT Sandbox làm môi trường kiểm thử chủ động

#### 5.2.2. Cross-dataset Generalization
- Chứng minh nguyên lý kiểm chứng hành vi tổng quát
- CIC-IoT-2023 và ToN-IoT cho cùng kết quả

#### 5.2.3. Giải pháp đồng thời ba vấn đề
- Pipeline 4 lớp: Phòng thủ + Giảm FPR
- DT-PW + Effort Gate: Phát hiện free-rider

#### 5.2.4. Framework triển khai được
- Overhead thấp, phù hợp hệ thống thực tế
- Sandbox isolation mang lại nhiều lợi ích

#### 5.2.5. Hướng dẫn chọn mô hình sinh dữ liệu
- TabDDPM đạt composite score cao nhất
- Áp dụng được cho các ứng dụng DT-FL khác

### 5.3. Các hạn chế của hệ thống
#### 5.3.1. Hạn chế về chi phí
- Overhead tăng tuyến tính theo số client
- Với N rất lớn, có thể cần tối ưu thêm

#### 5.3.2. Hạn chế về bộ sinh dữ liệu
- Phụ thuộc chất lượng TabDDPM
- Nếu challenge data kém, verification kém

#### 5.3.3. Hạn chế về đánh giá
- Chưa thử nghiệm trên mạng IoT thực tế
- Chỉ đánh giá 5 loại tấn công
- Không đánh giá các tấn công inference, model extraction

#### 5.3.4. Hạn chế về triển khai
- Chưa tích hợp Blockchain cho audit log
- Chưa đánh giá trong môi trường asynchronous FL

### 5.4. Hướng phát triển tiếp theo
#### 5.4.1. Tối ưu hóa TabDDPM
- Tăng tốc độ sinh, giảm latency
- Tăng fidelity và diversity

#### 5.4.2. Tích hợp Blockchain
- Audit log bất biến cho các bản cập nhật
- Theo dõi reputation client dài hạn

#### 5.4.3. Đánh giá trên mạng IoT thực
- Triển khai trên testbed IoT quy mô nhỏ
- Đánh giá trong điều kiện thực tế

#### 5.4.4. Mở rộng kịch bản tấn công
- Thêm: Inference attacks, model extraction, evasion attacks
- Đánh giá trong môi trường asynchronous FL

#### 5.4.5. Tối ưu hóa cho quy mô lớn
- Parallel verification nhiều clients
- Distributed DT Sandbox

### 5.5. Kế hoạch hoàn thiện
#### 5.5.1. Hoàn thiện bài báo khoa học quốc tế
- Nộp cho IEEE ICCE 2026
- Xây dựng slide và video demo

#### 5.5.2. Chuẩn bị bảo vệ luận văn
- Hoàn thiện luận văn theo định dạng chuẩn
- Chuẩn bị slide thuyết trình
- Mô phỏng bảo vệ

### 5.6. Tổng kết luận văn
- Khẳng định lại các kết quả và đóng góp
- Triển vọng nghiên cứu trong tương lai

---

## TÀI LIỆU THAM KHẢO

(Để danh sách 17 tài liệu từ references.bib theo đúng format)

---

## PHỤ LỤC

### Phụ lục A: Chi tiết thuật toán DT-Guard
- Thuật toán 1: DT Verification Pipeline
- Thuật toán 2: DT-PW Scoring
- Thuật toán 3: Effort Gate

### Phụ lục B: Mã nguồn chính
- Các function quan trọng trong DT-Guard

### Phụ lục C: Dữ liệu thực nghiệm đầy đủ
- Bảng kết quả chi tiết cho từng kịch bản
