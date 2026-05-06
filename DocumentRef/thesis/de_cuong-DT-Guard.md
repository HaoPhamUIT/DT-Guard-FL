ĐỀ CƯƠNG ĐỀ TÀI LUẬN VĂN THẠC SĨ

1. Giới thiệu và mục tiêu
Học liên kết (Federated Learning – FL) cho phép các thiết bị IoT cùng huấn luyện mô hình mà không cần chia sẻ dữ liệu thô, đáp ứng tốt các yêu cầu về quyền riêng tư và tiết kiệm băng thông. Tuy nhiên, trong thực tế IoT – nơi dữ liệu thường là Non‑IID và mất cân bằng lớp nghiêm trọng – FL rất dễ bị khai thác bởi các tấn công poisoning và backdoor (Backdoor, LIE, Min‑Max, Min‑Sum, MPAF). Các nghiên cứu gần đây cho thấy chưa có phương pháp phòng thủ nào duy trì được hiệu năng tốt trước các kịch bản tấn công tinh vi – mỗi cách tiếp cận đều bộc lộ điểm yếu trước ít nhất một dạng tấn công nhất định.
Đề tài xuất phát từ ba khoảng trống:
(1) Các phương pháp phòng thủ hiện tại vẫn bộc lộ nhiều điểm yếu, dễ bị các cuộc tấn công đầu độc ngày càng tinh vi – bao gồm LIE [6], Min‑Max/Min‑Sum [7], MPAF và Backdoor – qua mặt. Phân tích đối sánh trong DT‑BFL [1] và các nghiên cứu gần đây cho thấy mỗi phương pháp – dù là Krum [10], Median/Trimmed Mean [11], GeoMed [12], SignGuard [8], ClipCluster [9] hay LUP – đều thất bại trước ít nhất một loại tấn công khi được đánh giá trên cùng bộ dữ liệu thực tế;
(2) Phân tích tham số thụ động dễ nhầm lẫn giữa sai lệch tự nhiên do Non‑IID và hành vi cố tình phá hoại: SignGuard [8] dựa trên chiều dấu gradient, ClipCluster [9] dựa trên norm và phân cụm, LUP [1] dựa trên MAD và khoảng cách tham số – tất cả đều chỉ phân tích đặc trưng tĩnh của tham số mô hình mà không quan sát hành vi suy luận thực tế, khiến chúng dễ phát sinh tỷ lệ dương tính giả (FPR) cao hoặc bỏ lọt các tấn công đã được "tối ưu ngược" để nằm trong vùng phân phối bình thường như LIE [6], Min‑Max/Min‑Sum [7];
(3) Chưa có cơ chế định lượng mức đóng góp tri thức thực tế của từng client: FedAvg [10] gán trọng số theo số mẫu mà không phản ánh chất lượng; Trust Score trong LUP [1] và PoC trong PPSG [2] đánh giá dựa trên độ lệch tham số nhưng vô tình thưởng cho free‑rider vì bản cập nhật của chúng gần trùng với mô hình toàn cục.
Mục tiêu: 
(i) Xây dựng khung DT‑Guard, trong đó Digital Twin đóng vai trò "phòng thử nghiệm ảo" để chủ động kiểm chứng hành vi từng mô hình cục bộ, đồng thời tích hợp cơ chế tổng hợp DT‑PW để đo lường đóng góp tri thức thực tế và loại bỏ free‑rider.
(ii) Đánh giá toàn diện trên CIC‑IoT‑2023 [5] / ToN_IoT [15], so sánh với các phương pháp phòng thủ tiêu biểu hiện nay về độ chính xác, khả năng phát hiện, tỉ lệ dương tính giả, và tính công bằng đóng góp.
2. Nội dung nghiên cứu
Phân tích bài toán: Rà soát các nghiên cứu về FL cho IoT IDS, các hình thức tấn công poisoning/backdoor tiên tiến [6][7], cũng như hạn chế của các phương pháp phòng thủ hiện có (LUP [1], ClipCluster [9], SignGuard [8], GeoMed [12], PoC [2], Krum [13], Median, Trimmed Mean [11]) và các framework DT‑FL [1][2], blockchain‑FL gần đây. 
Xây dựng khung DT‑Guard: 
Trong hệ thống FL‑IDS, server không có quyền truy cập dữ liệu của client, nên không thể trực tiếp kiểm tra mô hình cục bộ có đáng tin hay không. Nếu chỉ phân tích tham số mô hình một cách thụ động thì dễ nhầm lẫn giữa sai lệch do Non‑IID và hành vi đầu độc [6][7]. Vì vậy, đề tài đưa Digital Twin vào phía server như một môi trường thử nghiệm an toàn, được tách biệt khỏi FL Server chính (nhằm cách ly hành vi độc hại tiềm tàng và cho phép kiểm chứng song song không ảnh hưởng vòng lặp chính). Mỗi vòng FL, DT‑Guard thực hiện 5 bước: (1) Upload – client gửi bản cập nhật lên FL Server; (2) Deploy – server triển khai mô hình vào Digital Twin Sandbox, chạy trên dữ liệu thách thức do bộ sinh chuyên biệt tạo ra; (3) Gate & Aggregate – hai cơ chế kiểm chứng (mô tả bên dưới) cho ra Trust‑Score và Performance‑Score, quyết định chấp nhận hay loại bỏ; (4) Update – mô hình toàn cục mới được tổng hợp từ các bản cập nhật đạt chuẩn; (5) Broadcast – phân phối lại cho các client.
Cơ chế 1 Pipeline kiểm định 4 lớp: Trust‑Score (giải quyết khoảng trống 1 & 2): Mỗi khi client gửi bản cập nhật mô hình lên, thay vì chấp nhận ngay, server đưa mô hình đó vào Digital Twin để chủ động kiểm tra hành vi thực tế qua bốn lớp kiểm định: (i) hiệu năng phát hiện xâm nhập trên dữ liệu thách thức; (ii) khả năng kháng backdoor, phát hiện qua độ lệch chuẩn bất thường của softmax confidence; (iii) mức lệch tham số so với mô hình toàn cục; (iv) độ ổn định qua các vòng. Kết quả được tổng hợp thành một điểm tin cậy duy nhất (Trust‑Score) theo cơ chế thích ứng: khi mức lệch tham số thấp (balanced mode), hiệu năng IDS và độ tương đồng tham số đóng góp theo tỉ lệ có trọng số; khi mức lệch cao (strict mode), cả hai phải đồng thời đạt điểm cao. Client chỉ được chấp nhận khi Trust‑Score vượt ngưỡng tin cậy. Nhờ vậy, Digital Twin giúp chuyển từ phân tích thụ động sang kiểm chứng chủ động, phân biệt rõ ràng giữa client lành tính có dữ liệu Non‑IID tự nhiên và client đang cố tình đầu độc mô hình.
Cơ chế 2 DT‑PW & Effort Gate: Performance‑Score (giải quyết khoảng trống 3): Đây là cơ chế để xử lý free‑rider – những client gần như không học gì mà chỉ sao chép mô hình chung. Thay vì chỉ nhìn vào tham số mô hình, server đưa cả mô hình của client và mô hình chung vào Digital Twin, cho chúng dự đoán trên cùng một bộ dữ liệu thách thức rồi so sánh kết quả. Client thật sự huấn luyện trên dữ liệu riêng sẽ cho ra dự đoán khác so với mô hình chung; free‑rider chỉ sao chép mô hình chung nên dự đoán gần như y hệt. Effort Gate xác định ngưỡng thích ứng dựa trên trung bình và độ lệch chuẩn của mức khác biệt dự đoán trên tập client đã qua Trust gate: nếu dự đoán của client quá giống mô hình chung, client bị xem là free‑rider và điểm đóng góp bị đưa về không; nếu vượt qua ngưỡng, client được chấm Performance‑Score kết hợp năng lực phát hiện với mức đóng góp tri thức mới. Trọng số tổng hợp cuối cùng là tích Trust‑Score và Performance‑Score (chuẩn hóa), đảm bảo chỉ client vừa đáng tin vừa đóng góp thực chất mới có ảnh hưởng lên mô hình toàn cục.
Bộ sinh dữ liệu thách thức 
Bộ sinh dữ liệu thách thức là thành phần hạ tầng then chốt phục vụ cho cả hai cơ chế trên, quyết định trực tiếp chất lượng và độ phân biệt của toàn bộ quá trình kiểm định hành vi. Đề tài khảo sát có hệ thống các mô hình sinh dữ liệu học sâu tiên tiến chuyên biệt cho dữ liệu dạng bảng: nhóm Diffusion gồm TabDDPM [3] (SOTA cho dữ liệu bảng), TabSyn [16] (tối ưu luồng nhiễu dữ liệu hỗn hợp) và ForestDiffusion [17] (tích hợp thuật toán dạng cây); nhóm GAN gồm CTGAN [4] (tối ưu hóa riêng cho cấu trúc dữ liệu bảng) và WGAN-GP [18] (kiến trúc cải tiến với độ ổn định huấn luyện cao). Các mô hình được phân tích dựa trên bốn nhóm tiêu chí: độ trung thực phân phối (Fidelity), độ bao phủ và đa dạng mẫu (Coverage & Diversity), khả năng kiểm soát nhãn điều kiện (Conditional Control), và chi phí tính toán (Resource & Latency). Việc lựa chọn bộ sinh là bước chuẩn bị hạ tầng cần thiết (A/B testing) để đảm bảo DT‑Guard hoạt động hiệu quả.
3. Phương pháp và thực nghiệm
Khảo sát, phân tích các nghiên cứu liên quan và công nghệ nền tảng
Tổng hợp tài liệu: Hệ thống hóa kiến thức về Federated Learning (FL) [10], Digital Twin (DT) [1][2] và các cơ chế phòng thủ hiện đại cho IoT IDS.
Phân tích các hình thức tấn công: Đi sâu vào các kịch bản tấn công poisoning và backdoor tiên tiến: LIE [6], Min-Max, Min-Sum [7], MPAF, Backdoor.
Đánh giá giải pháp hiện hữu: Phân tích có hệ thống hạn chế của 9 phương pháp phòng thủ baseline và các framework DT-FL, Blockchain-FL gần đây để làm rõ 3 khoảng trống nghiên cứu.
Khảo sát mô hình sinh: Đánh giá các kiến trúc sinh dữ liệu dạng bảng (TabDDPM [3], TabSyn [16], ForestDiffusion [17], CTGAN [4], WGAN-GP [18]) dựa trên thư viện Synthcity [14] làm cơ sở lựa chọn bộ sinh dữ liệu thách thức cho Digital Twin.
Thiết kế và đề xuất hệ thống DT-Guard
Mô hình hóa kiến trúc: Thiết kế hệ thống theo cấu trúc module hóa gồm: FL Server [10], Digital Twin [1], bộ sinh dữ liệu thách thức [3][4], pipeline kiểm định hành vi 4 lớp và bộ tổng hợp Aggregator DT-PW.
Xây dựng Pipeline kiểm định 4 lớp: Thiết lập quy trình đánh giá mô hình cục bộ dựa trên: (i) Hiệu năng phát hiện xâm nhập; (ii) Khả năng kháng backdoor; (iii) Mức độ lệch tham số; (iv) Độ ổn định qua các vòng lặp.
Thiết kế cơ chế DT-PW & Effort Gate: Xây dựng thuật toán tính toán Performance Score và cơ chế Effort Gate nhằm định lượng mức đóng góp tri thức thực tế, từ đó phát hiện và loại bỏ các thiết bị không học (Free-riders).
Xác định luồng dữ liệu: Đặc tả giao thức giao tiếp và quy trình luân chuyển dữ liệu/mô hình giữa các thành phần trong hệ thống.
Hiện thực hệ thống và thực nghiệm đánh giá		
Cài đặt môi trường: Triển khai hệ thống bằng ngôn ngữ Python và thư viện PyTorch trên môi trường mô phỏng FL.
Kịch bản 1 (A/B Testing): Huấn luyện và so sánh các mô hình sinh (Diffusion vs. GAN) bằng thư viện Synthcity [14] để chọn ra bộ sinh tối ưu cho môi trường Digital Twin.
Kịch bản 2 (Đánh giá phòng thủ): Thiết lập mô phỏng với 20 clients trên tập dữ liệu CIC-IoT-2023 [5] hoặc ToN_IoT [15], sử dụng mô hình IoTAttackNet để đối soát hiệu năng của DT-Guard với 9 phương pháp baseline dưới 5 loại tấn công [6][7].
Kịch bản 3 (Đánh giá tính công bằng): Thực hiện so sánh cơ chế DT-PW với các chiến lược tổng hợp phổ biến như FedAvg [10], Trust-Score (LUP [1] /PoC [2]) và Uniform để minh chứng khả năng định lượng đóng góp.
Phân tích kết quả, đánh giá tác động và hạn chế
Trực quan hóa dữ liệu: Tổng hợp kết quả thông qua các chỉ số Accuracy, Detection Rate, FPR, biểu đồ phân bổ trọng số theo vai trò (free‑rider vs. client thật), và số liệu chi phí vận hành (Latency, Peak Memory).
Phân tích đánh đổi (Trade-off Analysis): Đánh giá sự đánh đổi giữa lợi ích an ninh thu được và chi phí tài nguyên hệ thống (Latency, CPU/RAM) khi tích hợp Digital Twin.
Tổng kết: Nhận diện các hạn chế còn tồn tại, đề xuất hướng phát triển tương lai. Hoàn thiện bản thảo bài báo khoa học và luận văn.
4. Thiết lập thực nghiệm
Kịch bản 1: Đánh giá và tối ưu bộ sinh dữ liệu (A/B Testing)
Nhằm xác định mô hình sinh mẫu tối ưu nhất cho Digital Twin, đề tài đối sánh 5 kiến trúc thuộc 2 nhóm:
Nhóm Diffusion: TabDDPM (SOTA cho dữ liệu bảng), TabSyn (tối ưu luồng nhiễu dữ liệu hỗn hợp) và ForestDiffusion (tích hợp thuật toán dạng cây).
Nhóm GAN: CTGAN (chuyên biệt xử lý biến phân loại) và WGAN-GP (mô hình đối sánh - Baseline).
Kịch bản 2: Đánh giá hiệu năng phòng thủ của hệ thống DT-Guard
Dữ liệu: Bộ dữ liệu CIC‑IoT‑2023/ToN_IoT, phân bổ cho 20 client.
Mô hình IDS: Kiến trúc IoTAttackNet, huấn luyện qua 20 vòng FL.
Tỉ lệ client độc hại: Thay đổi ở mức 10%, 20%, 40% và 50% để đánh giá khả năng chống chịu ở nhiều mức độ tấn công.
Các tấn công đầu độc: dự kiến 5 kiểu – Backdoor, LIE, Min‑Max, Min‑Sum và MPAF, bao phủ cả tấn công hướng dữ liệu lẫn hướng tham số.
Các phương pháp phòng thủ so sánh: FedAvg, Krum, Median, Trimmed Mean, GeoMed, SignGuard, ClipCluster, LUP và PoC.
Kịch bản 3: Đánh giá tính công bằng
Mục tiêu: Chứng minh DT-PW hiệu quả hơn các phương pháp truyền thống trong việc định lượng đóng góp.
Đối chứng: So sánh DT-PW với:
FedAvg: Trọng số dựa trên số lượng mẫu (Dễ bị tấn công).
Trust-Score thuần (LUP/PoC): Trọng số dựa trên độ tương đồng (Thưởng cho free-rider).
Uniform: Trọng số bằng nhau (Cào bằng chất lượng).
Phân tích đánh đổi (Trade-off Analysis): Đánh giá bài toán chi phí - lợi ích giữa DT-PW và các phương pháp đối chứng. Cụ thể, thực nghiệm sẽ so sánh mức độ tiêu tốn thời gian (Latency) và tài nguyên (CPU/RAM) tăng thêm khi phải chạy Digital Twin.
Các chỉ số đánh giá:
Nhóm 1 Chọn bộ sinh dữ liệu (Kịch bản 1): Composite score tổng hợp từ bốn nhóm tiêu chí: Fidelity (TSTR, Wasserstein, JSD), Coverage & Diversity (DCR, PRDC), Conditional Control (Label Accuracy qua Oracle), và Resource & Latency (Training Time, Generation Latency, CPU/RAM).
Nhóm 2  Sức chống chịu trước tấn công (Kịch bản 2): Accuracy (hiệu năng phát hiện xâm nhập dưới mỗi kịch bản tấn công); Detection Rate (tỉ lệ nhận diện chính xác client độc hại); FPR (tỉ lệ loại bỏ nhầm client lành tính).
Nhóm 3 Tính công bằng đóng góp (Kịch bản 3): Trọng số trung bình mỗi vòng theo vai trò (Per-client Aggregation Weights — free‑rider vs. client thật); Accuracy đạt được dưới mỗi chiến lược tổng hợp.
Nhóm 4  Chi phí vận hành DT‑Guard: Latency tăng thêm mỗi vòng (ms); Peak Memory (MB).
5. Kết quả dự kiến
Đề xuất khung phòng thủ thống nhất DT‑Guard (đóng góp chính): Xây dựng kiến trúc DT‑Guard cho FL-IDS, bao gồm Pipeline kiểm định 4 lớp (Trust‑Score) và DT‑PW & Effort Gate (Performance‑Score). Kết quả này lấp đầy khoảng trống của các phương pháp thụ động bằng cách chuyển dịch sang kiểm chứng chủ động thông qua Digital Twin, giải quyết đồng thời cả ba khoảng trống nghiên cứu trong một kiến trúc thống nhất.
Chứng minh hiệu năng vượt trội qua thực nghiệm: DT-Guard duy trì độ chính xác cao, Detection Rate cao nhất, và FPR gần 0% so với 9 baseline dưới 5 kịch bản tấn công ngay cả trong điều kiện Non-IID cực đoan.
Kiểm chứng tính tổng quát hóa: Đánh giá DT‑Guard trên hai bộ dữ liệu khác nhau (CIC‑IoT‑2023 và ToN_IoT) cùng nhiều tỉ lệ client độc hại (10%, 20%, 40%, 50%) để khẳng định khung đề xuất không phụ thuộc vào một dataset hay một kịch bản tấn công cụ thể.
Chứng minh tính công bằng đóng góp: DT‑PW phát hiện và gán trọng số bằng không cho 100% free‑rider, trong khi Trust‑Score thuần vô tình thưởng cho chúng. DT‑Guard giúp mô hình hội tụ nhanh hơn nhờ ưu tiên client đóng góp tri thức thực tế.
Sản phẩm khoa học và tài liệu: Báo cáo luận văn hoàn chỉnh; Mã nguồn (source code) phục vụ tái lập; Ít nhất một bản thảo bài báo khoa học quốc tế.
6. Tài liệu tham khảo
[1] A. Issa, M. A. Ferrag, and L. Maglaras, "DT-BFL: Digital Twins for Blockchain-enabled Federated Learning in Internet of Things networks," Ad Hoc Networks, vol. 165, p. 103632, Jan. 2025
[2] Y. Zhang et al., "Adaptive Asynchronous Federated Learning for Digital Twin Driven Smart Grid," IEEE Transactions on Smart Grid, vol. 16, no. 5, pp. 4120-4132, Sep. 2025.
[3] A. Kotelnikov et al., "TabDDPM: Modelling tabular data with diffusion models," in Proc. 40th International Conference on Machine Learning (ICML), 2023, pp. 17564-17579.
[4] L. Xu et al., "Modeling Tabular data using Conditional GAN," in Advances in Neural Information Processing Systems (NeurIPS), vol. 32, 2019.
[5] E. C. P. Neto et al., "CICIoT2023: A Real-Time Dataset and Benchmark for Large-Scale Attacks in IoT Environment," Sensors, vol. 23, no. 13, p. 5941, 2023.
[6] G. Baruch, M. Baruch, and Y. Goldberg, "A Little Is Enough: Circumventing Defenses for Distributed Learning," in Advances in Neural Information Processing Systems (NeurIPS), 2019, pp. 8632-8642.
[7] V. Shejwalkar and A. Houmansadr, "Manipulating the Byzantine: Optimizing Model Poisoning Attacks and Defenses for Federated Learning," in Proc. Network and Distributed System Security Symposium (NDSS), 2021.
[8] J. Xu et al., "SignGuard: Byzantine-tolerant Federated Learning through Collaborative Malicious Gradient Filtering," in Proc. IEEE 42nd International Conference on Distributed Computing Systems (ICDCS), 2022, pp. 1-12.
[9] L. Zeng et al., "ClipCluster: A Defense against Byzantine Attacks in Federated Learning," IEEE Transactions on Information Forensics and Security, vol. 19, pp. 1450-1465, 2024.
[10] B. McMahan et al., "Communication-Efficient Learning of Deep Networks from Decentralized Data," in Proc. 20th International Conference on Artificial Intelligence and Statistics (AISTATS), 2017, pp. 1273-1282.
[11] D. Yin et al., "Byzantine-Robust Distributed Learning: Towards Optimal Statistical Rates," in Proc. 35th International Conference on Machine Learning (ICML), 2018, pp. 5650-5659.
[12] K. Pillutla, S. M. Kakade, and Z. Harchaoui, "Robust Aggregation for Federated Learning," IEEE Transactions on Signal Processing, vol. 70, pp. 1141-1154, 2022.
[13] P. Blanchard et al., "Machine Learning with Adversaries: Byzantine Tolerant Gradient Descent," in Advances in Neural Information Processing Systems (NeurIPS), 2017, pp. 119-129.
[14] Z. Qian et al., "Synthcity: A library for generating and evaluating synthetic data for machine learning," arXiv preprint arXiv:2301.07577, 2023. [Online]. Available: https://synthcity.readthedocs.io/en/latest/
[15] N. Moustafa, "New Generations of Data-Driven Intrusion Detection Systems for Networked Systems," IEEE Access, vol. 9, pp. 2021-2035, 2021. 
[16] B. Zhao, et al., "TabSyn: Tabular Synthesis with Diffusion Models," in Proc. International Conference on Learning Representations (ICLR), 2024.
[17] A. Houweling and P. Reutemann, "ForestDiffusion: Forest-based Diffusion Models for Tabular Data," arXiv preprint arXiv:2309.09908, 2023.
[18] I. Gulrajani et al., "Improved Training of Wasserstein GANs," in Advances in Neural Information Processing Systems (NeurIPS), 2017.

Kế hoạch


