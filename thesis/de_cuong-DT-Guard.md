
## Thông tin đề tài

- **Tên tiếng Việt:** PHƯƠNG PHÁP XÁC MINH CHỦ ĐỘNG DỰA TRÊN BẢN SAO SỐ VỚI TRỌNG SỐ HIỆU NĂNG NHẰM NÂNG CAO TÍNH CHỐNG CHỊU CỦA HỌC LIÊN KẾT TRONG PHÁT HIỆN XÂM NHẬP IoT
- **Tên tiếng Anh:** ACTIVE DIGITAL TWIN VERIFICATION WITH PERFORMANCE WEIGHTING FOR ROBUST FEDERATED LEARNING IN IoT INTRUSION DETECTION
- **Hướng đề tài luận văn:** Định hướng nghiên cứu (18 TC) — Đối với Khóa 2021 trở về trước
- **Ngành học và Mã ngành:** Khoa học máy tính: 8480101

---

<h1 align="center">ĐỀ CƯƠNG ĐỀ TÀI LUẬN VĂN THẠC SĨ</h1>

---

## 1. Giới thiệu và mục tiêu

Học liên kết (Federated Learning – FL) cho phép các thiết bị IoT cùng huấn luyện mô hình mà không cần chia sẻ dữ liệu thô, đáp ứng tốt các yêu cầu về quyền riêng tư và tiết kiệm băng thông. Tuy nhiên, trong thực tế IoT – nơi dữ liệu thường là Non‑IID và mất cân bằng lớp nghiêm trọng – FL rất dễ bị khai thác bởi các tấn công poisoning và backdoor (Backdoor, LIE, Min‑Max, Min‑Sum, MPAF). Các nghiên cứu gần đây cho thấy chưa có phương pháp phòng thủ nào duy trì được hiệu năng tốt trước các kịch bản tấn công tinh vi – mỗi cách tiếp cận đều bộc lộ điểm yếu trước ít nhất một dạng tấn công nhất định.

### Ba khoảng trống nghiên cứu (Research Gaps)

**(1) Các phương pháp phòng thủ hiện tại còn nhiều điểm yếu:**
Dễ bị các cuộc tấn công đầu độc ngày càng tinh vi – bao gồm LIE [6], Min‑Max/Min‑Sum [7], MPAF và Backdoor – qua mặt. Phân tích đối sánh trong DT‑BFL [1] và các nghiên cứu gần đây cho thấy mỗi phương pháp – dù là Krum [10], Median/Trimmed Mean [11], GeoMed [12], SignGuard [8], ClipCluster [9] hay LUP – đều thất bại trước ít nhất một loại tấn công khi được đánh giá trên cùng bộ dữ liệu thực tế.

**(2) Phân tích tham số thụ động dễ nhầm lẫn giữa sai lệch tự nhiên do Non‑IID và hành vi cố tình phá hoại:**
SignGuard [8] dựa trên chiều dấu gradient, ClipCluster [9] dựa trên norm và phân cụm, LUP [1] dựa trên MAD và khoảng cách tham số – tất cả đều chỉ phân tích đặc trưng tĩnh của tham số mô hình mà không quan sát hành vi suy luận thực tế, khiến chúng dễ phát sinh tỷ lệ dương tính giả (FPR) cao hoặc bỏ lọt các tấn công đã được "tối ưu ngược" để nằm trong vùng phân phối bình thường như LIE [6], Min‑Max/Min‑Sum [7].

**(3) Chưa có cơ chế định lượng mức đóng góp tri thức thực tế của từng client:**
FedAvg [10] gán trọng số theo số mẫu mà không phản ánh chất lượng; Trust Score trong LUP [1] và PoC trong PPSG [2] đánh giá dựa trên độ lệch tham số nhưng vô tình thưởng cho free‑rider vì bản cập nhật của chúng gần trùng với mô hình toàn cục.

### Mục tiêu

> **(i)** Xây dựng khung **DT‑Guard**, trong đó Digital Twin đóng vai trò "phòng thử nghiệm ảo" để chủ động kiểm chứng hành vi từng mô hình cục bộ.
>
> **(ii)** Thiết kế cơ chế tổng hợp mô hình **DT-Driven Performance Weighting (DT-PW)**. Cơ chế này tận dụng Digital Twin như một "giám khảo" để chấm điểm năng lực thực tế của từng client trên dữ liệu thách thức, từ đó tối ưu hóa trọng số đóng góp và loại bỏ các hành vi đóng góp không giá trị.
>
> **(iii)** Đánh giá toàn diện trên CIC‑IoT‑2023 [5] / ToN\_IoT [15], so sánh với các phương pháp phòng thủ tiêu biểu hiện nay về độ chính xác, khả năng phát hiện, tỉ lệ dương tính giả, tỉ lệ lỗi.

---

## 2. Nội dung nghiên cứu

### 2.1. Phân tích bài toán

Rà soát các nghiên cứu về FL cho IoT IDS, các hình thức tấn công poisoning/backdoor tiên tiến [6][7], cũng như hạn chế của các phương pháp phòng thủ hiện có (LUP [1], ClipCluster [9], SignGuard [8], GeoMed [12], PoC [2], Krum [13], Median, Trimmed Mean [11]) và các framework DT‑FL [1][2], blockchain‑FL gần đây.

### 2.2. Xây dựng khung DT‑Guard

Trong hệ thống FL‑IDS, server không có quyền truy cập dữ liệu của client, nên không thể trực tiếp kiểm tra mô hình cục bộ có đáng tin hay không. Nếu chỉ phân tích tham số mô hình một cách thụ động thì dễ nhầm lẫn giữa sai lệch do Non‑IID và hành vi đầu độc [6][7].

Vì vậy, đề tài đưa **Digital Twin** vào phía server như một **môi trường thử nghiệm an toàn**, mô phỏng lại các dạng lưu lượng mạng IoT bình thường và tấn công thông qua **dữ liệu thách thức (challenge data)** được sinh ra bởi một bộ sinh chuyên biệt. Mỗi khi client gửi bản cập nhật mô hình lên, thay vì chấp nhận ngay, server đưa mô hình đó vào Digital Twin để chủ động kiểm tra hành vi thực tế qua **bốn lớp kiểm định**:

1. Hiệu năng phát hiện xâm nhập
2. Khả năng kháng backdoor
3. Mức lệch tham số
4. Độ ổn định qua các vòng

Kết quả được tổng hợp thành **một điểm tin cậy duy nhất**, dùng để quyết định bản cập nhật nào đủ điều kiện đưa vào bước tổng hợp mô hình. Nhờ vậy, Digital Twin giúp chuyển từ *phân tích thụ động* sang **kiểm chứng chủ động**, phân biệt rõ ràng giữa client lành tính có dữ liệu Non‑IID tự nhiên và client đang cố tình đầu độc mô hình.

### 2.3. Bộ sinh dữ liệu thách thức (Challenge Data Generator)

Bộ sinh dữ liệu thách thức là thành phần then chốt của Digital Twin, quyết định trực tiếp chất lượng và độ phân biệt của toàn bộ quá trình kiểm định hành vi. Đề tài khảo sát có hệ thống các mô hình sinh dữ liệu học sâu tiên tiến chuyên biệt cho dữ liệu dạng bảng:

| Nhóm | Mô hình | Đặc điểm |
| ---- | ------- | -------- |
| **Diffusion** | ForestDiffusion [17] | Tích hợp thuật toán dạng cây |
| **Diffusion** | TabSyn [16] | Tối ưu luồng nhiễu dữ liệu hỗn hợp |
| **Diffusion** | TabDDPM [3] | SOTA cho dữ liệu bảng |
| **GAN** | CTGAN [4] | Tối ưu hóa riêng cho cấu trúc dữ liệu bảng |
| **GAN** | WGAN-GP [18] | Kiến trúc cải tiến với độ ổn định huấn luyện cao |

Các mô hình được phân tích dựa trên **bốn nhóm tiêu chí cốt lõi**:
- Độ trung thực của phân phối (Fidelity)
- Độ bao phủ và đa dạng mẫu (Coverage & Diversity)
- Khả năng kiểm soát nhãn điều kiện (Conditional Control)
- Chi phí tính toán (Resource & Latency)

### 2.4. Cơ chế chấm điểm đóng góp DT-Driven Performance Weighting (DT-PW)

Đây là cơ chế để xử lý **free‑rider** – những client gần như không học gì mà chỉ sao chép mô hình chung.

**Cách đo đóng góp:**
Thay vì chỉ nhìn vào tham số mô hình, server đưa cả mô hình của client và mô hình chung vào Digital Twin, cho chúng dự đoán trên cùng một bộ dữ liệu thách thức rồi so sánh kết quả:

- ✅ Client thật sự huấn luyện trên dữ liệu riêng → dự đoán **khác** so với mô hình chung
- ❌ Free‑rider chỉ sao chép mô hình chung → dự đoán **gần như y hệt**

**Cổng nỗ lực (Effort Gate):**
Dựa trên mức độ khác nhau trong dự đoán, hệ thống tự động đặt một ngưỡng:

- Nếu dự đoán quá giống mô hình chung → client bị xem là **free‑rider**, điểm đóng góp = 0
- Nếu vượt qua ngưỡng → client được chấm điểm đóng góp **tỉ lệ với mức độ khác biệt** (tức là lượng tri thức mới mang lại)

---

## 3. Phương pháp và thực nghiệm

### 3.1. Khảo sát, phân tích các nghiên cứu liên quan và công nghệ nền tảng

- **Tổng hợp tài liệu:** Hệ thống hóa kiến thức về Federated Learning (FL) [10], Digital Twin (DT) [1][2] và các cơ chế phòng thủ hiện đại cho IoT IDS.
- **Phân tích các hình thức tấn công:** Đi sâu vào các kịch bản tấn công poisoning và backdoor tiên tiến: LIE [6], Min-Max, Min-Sum [7], MPAF, Backdoor.
- **Đánh giá giải pháp hiện hữu:** Phân tích có hệ thống hạn chế của 9 phương pháp phòng thủ baseline (LUP [1], ClipCluster [9], SignGuard [8], GeoMed [12], PoC [2], Krum [13], Median [11], Trimmed Mean [11]) và các framework DT-FL, Blockchain-FL gần đây để làm rõ 3 khoảng trống nghiên cứu.
- **Khảo sát mô hình sinh (Generative Models):** Đánh giá các kiến trúc sinh dữ liệu dạng bảng (TabDDPM [3], TabSyn [16], ForestDiffusion [17], CTGAN [4], WGAN-GP [18]) dựa trên thư viện Synthcity [14] làm cơ sở lựa chọn bộ sinh dữ liệu thách thức cho Digital Twin.

### 3.2. Thiết kế và đề xuất hệ thống DT-Guard

- **Mô hình hóa kiến trúc:** Thiết kế hệ thống theo cấu trúc module hóa gồm: FL Server [10], Digital Twin [1], bộ sinh dữ liệu thách thức [3][4], pipeline kiểm định hành vi 4 lớp và bộ tổng hợp Aggregator DT-PW.
- **Xây dựng Pipeline kiểm định 4 lớp:** Thiết lập quy trình đánh giá mô hình cục bộ dựa trên:
  1. Hiệu năng phát hiện xâm nhập
  2. Khả năng kháng backdoor
  3. Mức độ lệch tham số
  4. Độ ổn định qua các vòng lặp
- **Thiết kế cơ chế DT-PW & Effort Gate:** Xây dựng thuật toán tính toán Performance Score và cơ chế Effort Gate nhằm định lượng mức đóng góp tri thức thực tế, từ đó phát hiện và loại bỏ các thiết bị không học (Free-riders).
- **Xác định luồng dữ liệu:** Đặc tả giao thức giao tiếp và quy trình luân chuyển dữ liệu/mô hình giữa các thành phần trong hệ thống.

### 3.3. Hiện thực hệ thống và thực nghiệm đánh giá

- **Cài đặt môi trường:** Triển khai hệ thống bằng Python và thư viện PyTorch trên môi trường mô phỏng FL.
- **Kịch bản 1 (A/B Testing):** Huấn luyện và so sánh các mô hình sinh (Diffusion vs. GAN) bằng thư viện Synthcity [14] để chọn ra bộ sinh tối ưu cho Digital Twin.
- **Kịch bản 2 (Đánh giá phòng thủ):** Thiết lập mô phỏng với 20 clients trên tập dữ liệu CIC-IoT-2023 [5] hoặc ToN\_IoT [15], sử dụng mô hình IoTAttackNet để đối soát hiệu năng của DT-Guard với 9 phương pháp baseline dưới 5 loại tấn công [6][7].
- **Kịch bản 3 (Đánh giá tính công bằng):** Thực hiện so sánh cơ chế DT-PW với các chiến lược tổng hợp phổ biến như FedAvg [10], Trust-Score (LUP [1] / PoC [2]) và Uniform để minh chứng khả năng định lượng đóng góp.

### 3.4. Phân tích kết quả, đánh giá tác động và hạn chế

- **Trực quan hóa dữ liệu:** Tổng hợp kết quả thông qua các chỉ số Accuracy, FPR, Detection Rate [5][15], đường cong hội tụ và biểu đồ phân bổ trọng số.
- **Phân tích đánh đổi (Trade-off Analysis):** Đánh giá sự đánh đổi giữa lợi ích an ninh thu được và chi phí tài nguyên hệ thống (Latency, CPU/RAM) khi tích hợp Digital Twin.
- **Nghiên cứu bóc tách (Ablation Study):** Đánh giá tầm quan trọng của từng thành phần: bộ sinh dữ liệu, pipeline 4 lớp và cơ chế Effort Gate đối với tổng thể hệ thống.
- **Tổng kết và công bố:** Nhận diện các hạn chế còn tồn tại, đề xuất hướng phát triển tương lai. Hoàn thiện bản thảo bài báo khoa học và hoàn thiện luận văn.

---

## 4. Thiết lập thực nghiệm

### Kịch bản 1: Đánh giá và tối ưu bộ sinh dữ liệu (A/B Testing)

Nhằm xác định mô hình sinh mẫu tối ưu nhất cho Digital Twin, đề tài đối sánh **5 kiến trúc thuộc 2 nhóm**:

- **Nhóm Diffusion:** TabDDPM (SOTA cho dữ liệu bảng), TabSyn (tối ưu luồng nhiễu dữ liệu hỗn hợp) và ForestDiffusion (tích hợp thuật toán dạng cây).
- **Nhóm GAN:** CTGAN (chuyên biệt xử lý biến phân loại) và WGAN-GP (mô hình đối sánh - Baseline).

### Kịch bản 2: Đánh giá hiệu năng phòng thủ của hệ thống DT-Guard

| Thông số | Giá trị |
| -------- | ------- |
| **Dữ liệu** | CIC‑IoT‑2023 / ToN\_IoT, phân bổ cho 20 client |
| **Mô hình IDS** | IoTAttackNet, huấn luyện qua 20 vòng FL |
| **Tỉ lệ client độc hại** | 10%, 20%, 40%, 50% |
| **Tấn công đầu độc** | Backdoor, LIE, Min‑Max, Min‑Sum, MPAF |
| **Phương pháp phòng thủ so sánh** | FedAvg, Krum, Median, Trimmed Mean, GeoMed, SignGuard, ClipCluster, LUP, PoC |

### Kịch bản 3: Đánh giá tính công bằng

**Mục tiêu:** Chứng minh DT-PW hiệu quả hơn các phương pháp truyền thống trong việc định lượng đóng góp.

**Đối chứng — So sánh DT-PW với:**

| Phương pháp | Cơ chế | Hạn chế |
| ----------- | ------ | ------- |
| FedAvg | Trọng số dựa trên số lượng mẫu | Dễ bị tấn công |
| Trust-Score thuần (LUP/PoC) | Trọng số dựa trên độ tương đồng | Thưởng cho free-rider |
| Uniform | Trọng số bằng nhau | Cào bằng chất lượng |

**Phân tích đánh đổi (Trade-off Analysis):**
Đánh giá bài toán chi phí - lợi ích giữa DT-PW và các phương pháp đối chứng. Cụ thể, thực nghiệm sẽ so sánh mức độ tiêu tốn thời gian (Latency) và tài nguyên (CPU/RAM) tăng thêm khi phải chạy Digital Twin.

### Các chỉ số đánh giá

#### Nhóm 1 — Chỉ số tối ưu bộ sinh dữ liệu

| Chỉ số | Mô tả |
| ------ | ----- |
| **Độ trung thực (Fidelity)** | Đo lường hiệu năng phân loại chéo qua chỉ số TSTR (Train on Synthetic, Test on Real), kết hợp đánh giá sự sai lệch phân phối bằng khoảng cách Wasserstein (biến liên tục) và Jensen-Shannon Distance (JSD - biến phân loại). |
| **Độ bao phủ và đa dạng (Coverage & Diversity)** | Đánh giá mức độ ghi nhớ dữ liệu qua khoảng cách DCR (Distance to Closest Record) và hệ chỉ số PRDC (Precision, Recall, Density, Coverage) nhằm đảm bảo mô hình sinh mẫu tấn công đa dạng, tránh hiện tượng sập mode. |
| **Kiểm soát điều kiện (Conditional Control)** | Đo lường độ chính xác nhãn giả định (Label Accuracy) thông qua việc kiểm chứng bằng một mô hình IDS chuẩn (Oracle). |
| **Chi phí tính toán (Resource & Latency)** | So sánh thời gian huấn luyện (Training Time), độ trễ sinh mẫu (Generation Latency) và mức chiếm dụng CPU/RAM để đánh giá tính khả thi khi tích hợp vào vòng lặp FL. |

#### Nhóm 2 — Chỉ số hiệu năng FL-IDS

| Chỉ số | Mô tả |
| ------ | ----- |
| **Accuracy & Error Rate** | Hiệu năng phát hiện xâm nhập dưới mỗi kịch bản tấn công và mức suy giảm so với base. |
| **Detection Rate & FPR** | Khả năng của Digital Twin nhận diện chính xác client độc hại và tỉ lệ loại bỏ nhầm client lành tính. |

#### Nhóm 3 — Chỉ số đánh giá tính công bằng và đóng góp

| Chỉ số | Mô tả |
| ------ | ----- |
| **Trọng số trung bình theo vai trò (Average Weight by Role)** | Đo lường và đối sánh mức trọng số trung bình mà các chiến lược gán cho từng nhóm client (Free-Rider, Normal). Chỉ số cốt lõi để minh chứng khả năng nhận diện hành vi lười biếng của DT-PW. |
| **Đường cong hội tụ (Convergence Curve)** | Theo dõi sự biến thiên của Accuracy qua từng vòng lặp FL của các chiến lược đối chứng, qua đó khẳng định DT-PW giúp mô hình chung hội tụ nhanh và duy trì độ ổn định tốt hơn. |
| **Biểu đồ phân bổ trọng số (Weight Distribution)** | Trực quan hóa sự phân bổ trọng số chi tiết của từng client dưới các phương pháp tiếp cận khác nhau (DT-PW, Shapley, Trust-Score, Uniform) nhằm làm rõ năng lực phân biệt giữa đóng góp thực chất và đóng góp rỗng. |
| **Chi phí tính toán (Latency & Resource Consumption)** | Đo lường độ trễ tổng hợp (Aggregation Latency) và mức chiếm dụng phần cứng (CPU/RAM) trong quá trình chấm điểm. Trực quan hóa bài toán đánh đổi giữa chi phí tăng thêm của DT-PW so với các baseline và lợi ích công bằng thu lại được. |

---

## 5. Kết quả dự kiến

1. **Hệ thống hóa thành công khung phòng thủ DT‑Guard:** Đề xuất và xây dựng kiến trúc DT‑Guard cho FL-IDS. Kết quả này lấp đầy khoảng trống của các phương pháp thụ động bằng cách chuyển dịch sang kiểm chứng chủ động thông qua Digital Twin, phân biệt rõ ràng giữa sai lệch do Non-IID tự nhiên và hành vi phá hoại.

2. **Thiết lập cơ chế tổng hợp tối ưu DT-PW:** Hoàn thiện thuật toán định lượng đóng góp dựa trên hiệu năng thực tế. Cơ chế này loại bỏ hoàn toàn tác động của các Free-riders và ưu tiên các Client ưu tú, từ đó đẩy nhanh tốc độ hội tụ.

3. **Chứng minh hiệu năng vượt trội qua thực nghiệm:** Bảng phân tích khẳng định sức chống chịu của DT-Guard trước 5 kịch bản tấn công (Backdoor, LIE, Min‑Max, Min‑Sum, MPAF). Duy trì độ chính xác cao, giảm thiểu tỉ lệ lỗi và giữ FPR ở mức thấp nhất so với 9 phương pháp baseline hiện có ngay cả trong điều kiện Non-IID cực đoan.

4. **Hoàn thiện các module tối ưu hóa chuyên sâu:** Đảm bảo tính khả thi của hệ thống bao gồm cơ chế tổng hợp dung hợp giữa Performance-Score và Trust-Score; hoàn tất đánh giá đối sánh chọn ra mô hình sinh dữ liệu dạng bảng tốt nhất cho môi trường Digital Twin.

5. **Sản phẩm khoa học và tài liệu:**
   - Báo cáo luận văn hoàn chỉnh
   - Mã nguồn (source code) phục vụ tái lập
   - Ít nhất một bản thảo bài báo khoa học quốc tế

---

## 6. Tài liệu tham khảo

| # | Tham khảo |
|---|-----------|
| [1] | A. Issa, M. A. Ferrag, and L. Maglaras, "DT-BFL: Digital Twins for Blockchain-enabled Federated Learning in Internet of Things networks," *Ad Hoc Networks*, vol. 165, p. 103632, Jan. 2025. |
| [2] | Y. Zhang et al., "Adaptive Asynchronous Federated Learning for Digital Twin Driven Smart Grid," *IEEE Transactions on Smart Grid*, vol. 16, no. 5, pp. 4120-4132, Sep. 2025. |
| [3] | A. Kotelnikov et al., "TabDDPM: Modelling tabular data with diffusion models," in *Proc. 40th ICML*, 2023, pp. 17564-17579. |
| [4] | L. Xu et al., "Modeling Tabular data using Conditional GAN," in *NeurIPS*, vol. 32, 2019. |
| [5] | E. C. P. Neto et al., "CICIoT2023: A Real-Time Dataset and Benchmark for Large-Scale Attacks in IoT Environment," *Sensors*, vol. 23, no. 13, p. 5941, 2023. |
| [6] | G. Baruch, M. Baruch, and Y. Goldberg, "A Little Is Enough: Circumventing Defenses for Distributed Learning," in *NeurIPS*, 2019, pp. 8632-8642. |
| [7] | V. Shejwalkar and A. Houmansadr, "Manipulating the Byzantine: Optimizing Model Poisoning Attacks and Defenses for Federated Learning," in *Proc. NDSS*, 2021. |
| [8] | J. Xu et al., "SignGuard: Byzantine-tolerant Federated Learning through Collaborative Malicious Gradient Filtering," in *Proc. IEEE 42nd ICDCS*, 2022, pp. 1-12. |
| [9] | L. Zeng et al., "ClipCluster: A Defense against Byzantine Attacks in Federated Learning," *IEEE TIFS*, vol. 19, pp. 1450-1465, 2024. |
| [10] | B. McMahan et al., "Communication-Efficient Learning of Deep Networks from Decentralized Data," in *Proc. 20th AISTATS*, 2017, pp. 1273-1282. |
| [11] | D. Yin et al., "Byzantine-Robust Distributed Learning: Towards Optimal Statistical Rates," in *Proc. 35th ICML*, 2018, pp. 5650-5659. |
| [12] | K. Pillutla, S. M. Kakade, and Z. Harchaoui, "Robust Aggregation for Federated Learning," *IEEE TSP*, vol. 70, pp. 1141-1154, 2022. |
| [13] | P. Blanchard et al., "Machine Learning with Adversaries: Byzantine Tolerant Gradient Descent," in *NeurIPS*, 2017, pp. 119-129. |
| [14] | Z. Qian et al., "Synthcity: A library for generating and evaluating synthetic data for machine learning," *arXiv:2301.07577*, 2023. [Online](https://synthcity.readthedocs.io/en/latest/) |
| [15] | N. Moustafa, "New Generations of Data-Driven Intrusion Detection Systems for Networked Systems," *IEEE Access*, vol. 9, pp. 2021-2035, 2021. |
| [16] | B. Zhao et al., "TabSyn: Tabular Synthesis with Diffusion Models," in *Proc. ICLR*, 2024. |
| [17] | A. Houweling and P. Reutemann, "ForestDiffusion: Forest-based Diffusion Models for Tabular Data," *arXiv:2309.09908*, 2023. |
| [18] | I. Gulrajani et al., "Improved Training of Wasserstein GANs," in *NeurIPS*, 2017. |

---

## 7. Kế hoạch thực hiện

| Tháng | Nội dung | T1 | T2 | T3 | T4 | T5 | T6 |
| :---: | -------- | :-: | :-: | :-: | :-: | :-: | :-: |
| **1** | **Khảo sát & Chuẩn bị** | ✅ | ✅ | | | | |
| | - Hệ thống hóa lý thuyết FL, DT và các tấn công (LIE, Min-Max...) | | | | | | |
| | - Khảo sát 5 kiến trúc sinh dữ liệu bảng (TabDDPM, CTGAN...) | | | | | | |
| | - Tiền xử lý dữ liệu CIC-IoT-2023 & ToN\_IoT | | | | | | |
| **2** | **Thiết kế hệ thống** | | ✅ | ✅ | | | |
| | - Mô hình hóa kiến trúc module (Server, DT, Aggregator) | | | | | | |
| | - Thiết lập logic Pipeline kiểm định 4 lớp | | | | | | |
| | - Thiết kế thuật toán DT-PW và cơ chế Effort Gate | | | | | | |
| **3** | **Hiện thực & Kịch bản 1** | | | ✅ | ✅ | | |
| | - Cài đặt môi trường Python/PyTorch/Synthcity | | | | | | |
| | - Thực hiện Kịch bản 1: Đối soát Diffusion vs GAN (A/B Testing) | | | | | | |
| | - Chọn bộ sinh tối ưu cho Digital Twin | | | | | | |
| **4** | **Thực nghiệm diện rộng** | | | | ✅ | | |
| | - Thực hiện Kịch bản 2: Mô phỏng FL 20 clients với 5 loại tấn công | | | | | | |
| | - Thực hiện Kịch bản 3: Đối soát DT-PW với FedAvg, LUP, PoC, Uniform | | | | | | |
| | - Thu thập chỉ số Accuracy, FPR, Latency, CPU/RAM | | | | | | |
| **5** | **Phân tích & Đánh giá** | | | | | ✅ | ✅ |
| | - Xử lý số liệu, vẽ biểu đồ hội tụ và phân bổ trọng số | | | | | | |
| | - Thực hiện Ablation Study | | | | | | |
| | - Phân tích Trade-off giữa an ninh và tài nguyên | | | | | | |
| **6** | **Tổng hợp kết quả, viết báo cáo và bảo vệ** | | | | | | ✅ |
| | - Viết bản thảo bài báo khoa học | | | | | | |
| | - Chỉnh sửa, hoàn thiện toàn văn luận văn Thạc sĩ | | | | | | |
| | - Chuẩn bị hồ sơ bảo vệ | | | | | | |
