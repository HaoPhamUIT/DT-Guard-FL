ĐẠI HỌC QUỐC GIA TP. HỒ CHÍ MINH
TRƯỜNG ĐẠI HỌC
CÔNG NGHỆ THÔNG TIN
CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM
Độc Lập - Tự Do - Hạnh Phúc


PHIẾU ĐĂNG KÝ 
PHƯƠNG THỨC ĐÀO TẠO VÀ ĐỀ TÀI LUẬN VĂN THẠC SĨ

Tên đề tài:
Tên tiếng Việt: PHƯƠNG PHÁP XÁC MINH CHỦ ĐỘNG DỰA TRÊN BẢN SAO SỐ VỚI TRỌNG SỐ DỰA TRÊN HIỆU NĂNG NHẰM NÂNG CAO TÍNH CHỐNG CHỊU CỦA HỌC LIÊN KẾT TRONG PHÁT HIỆN XÂM NHẬP IoT
Tên tiếng Anh: ACTIVE DIGITAL TWIN VERIFICATION  WITH PERFORMANCE WEIGHTING FOR ROBUST FEDERATED LEARNING IN IoT INTRUSION DETECTION
Hướng đề tài luận văn: Đối với Khóa 2021 trở về trước
Định hướng nghiên cứu	(18 TC)		
Ngành học và Mã ngành: 
Khoa học máy tính: 8480101
Cán bộ hướng dẫn:
Họ tên: TS. Phan Thế Duy
Email: duypt@uit.edu.vn
Điện thoại:
Đơn vị công tác: Phòng thí nghiệm An Toàn Thông Tin, Trường Đại Học Công Nghệ Thông tin - ĐHQG-HCM.
Thời gian thực hiện: 6 tháng. Từ tháng 11/2025
Học viên thực hiện:
Họ tên: Phạm Hoàng Hảo
Mã số: CH21210101005	Khóa: 16		Đợt: 2021
Email: haoph.16@grad.uit.edu.vn	Điện thoại: 0943861619

Xác nhận của CBHD
(Ký tên và ghi rõ họ tên)
TP. HCM, ngày 28 tháng 03 năm 2026
Học viên
(Ký tên và ghi rõ họ tên)









ĐỀ CƯƠNG ĐỀ TÀI LUẬN VĂN THẠC SĨ

1. Giới thiệu và mục tiêu
Học liên kết (Federated Learning – FL) cho phép các thiết bị IoT cùng huấn luyện mô hình mà không cần chia sẻ dữ liệu thô, đáp ứng tốt các yêu cầu về quyền riêng tư và tiết kiệm băng thông [10]. Tuy nhiên, trong thực tế IoT – nơi dữ liệu thường Non‑IID và mất cân bằng lớp nghiêm trọng – FL rất dễ bị khai thác bởi các tấn công poisoning và backdoor [6][7]. Các nghiên cứu gần đây [1][8][9] cho thấy chưa có phương pháp phòng thủ nào duy trì được hiệu năng tốt trước các kịch bản tấn công tinh vi – mỗi cách tiếp cận đều bộc lộ điểm yếu trước ít nhất một dạng tấn công nhất định.
Đề tài xuất phát từ ba khoảng trống:
(1) Các phương pháp phòng thủ hiện tại vẫn bộc lộ nhiều điểm yếu, dễ bị các cuộc tấn công đầu độc ngày càng tinh vi – bao gồm LIE [6], Min‑Max/Min‑Sum [7], MPAF và Backdoor – qua mặt. Phân tích đối sánh trong DT‑BFL [1] và các nghiên cứu gần đây cho thấy mỗi phương pháp – dù là Krum [10], Median/Trimmed Mean [11], GeoMed [12], SignGuard [8], ClipCluster [9] hay LUP – đều thất bại trước ít nhất một loại tấn công khi được đánh giá trên cùng bộ dữ liệu thực tế;

(2) Phân tích tham số thụ động dễ nhầm lẫn giữa sai lệch tự nhiên do Non‑IID và hành vi cố tình phá hoại: SignGuard [8] dựa trên chiều dấu gradient, ClipCluster [9] dựa trên norm và phân cụm, LUP [1] dựa trên MAD và khoảng cách tham số. Khiến các hệ thống này dễ phát sinh tỷ lệ dương tính giả (FPR) cao hoặc bỏ lọt các tấn công đã được tối ưu ngược như LIE [6], Min‑Max/Min‑Sum [7];
(3) Chưa có cơ chế định lượng mức đóng góp tri thức thực tế của từng client: FedAvg [10] gán trọng số theo số mẫu mà không phản ánh chất lượng; Trust Score trong LUP [1] và PoC trong PPSG [2] đánh giá dựa trên độ lệch tham số nhưng vô tình thưởng cho free‑rider vì bản cập nhật của chúng gần trùng với mô hình toàn cục.
Mục tiêu:
(i) Xây dựng khung DT‑Guard, trong đó Digital Twin đóng vai trò "phòng thử nghiệm ảo" để chủ động kiểm chứng hành vi từng mô hình cục bộ;
(ii) Thiết kế cơ chế tổng hợp mô hình DT-Driven Performance Weighting (DT-PW). Cơ chế này tận dụng Digital Twin như một "giám khảo" để chấm điểm năng lực thực tế của từng client trên dữ liệu thách thức, từ đó tối ưu hóa trọng số đóng góp và loại bỏ các hành vi đóng góp không giá trị;
(iii) Đánh giá toàn diện trên CIC‑IoT‑2023 [5]/ToN_IoT, so sánh với các phương pháp phòng thủ tiêu biểu hiện nay về độ chính xác, khả năng phát hiện, tỉ lệ dương tính giả, tỉ lệ lỗi.
2. Nội dung nghiên cứu
Phân tích bài toán: Rà soát các nghiên cứu về FL cho IoT IDS, các hình thức tấn công poisoning/backdoor tiên tiến, cũng như hạn chế của các phương pháp phòng thủ hiện có (LUP, ClipCluster, SignGuard, GeoMed, PoC, Krum, Median, Trimmed Mean) và các framework DT‑FL, blockchain‑FL gần đây.
Xây dựng khung DT‑Guard: Trong hệ thống FL‑IDS, server không có quyền truy cập dữ liệu của client, nên không thể trực tiếp kiểm tra mô hình cục bộ có đáng tin hay không. Nếu chỉ phân tích tham số mô hình một cách thụ động thì dễ nhầm lẫn giữa sai lệch do Non‑IID và hành vi đầu độc. Vì vậy, đề tài đưa Digital Twin vào phía server như một môi trường thử nghiệm an toàn, mô phỏng lại các dạng lưu lượng mạng IoT bình thường và tấn công thông qua dữ liệu thách thức (challenge data) được sinh ra bởi một bộ sinh chuyên biệt. Mỗi khi client gửi bản cập nhật mô hình lên, thay vì chấp nhận ngay, server đưa mô hình đó vào Digital Twin để chủ động kiểm tra hành vi thực tế qua bốn lớp kiểm định: hiệu năng phát hiện xâm nhập, khả năng kháng backdoor, mức lệch tham số và độ ổn định qua các vòng. Kết quả được tổng hợp thành một điểm tin cậy duy nhất, dùng để quyết định bản cập nhật nào đủ điều kiện đưa vào bước tổng hợp mô hình. Nhờ vậy, Digital Twin giúp chuyển từ phân tích thụ động sang kiểm chứng chủ động, phân biệt rõ ràng giữa client lành tính có dữ liệu Non‑IID tự nhiên và client đang cố tình đầu độc mô hình.
Bộ sinh dữ liệu thách thức là thành phần then chốt của Digital Twin, quyết định trực tiếp chất lượng và độ phân biệt của toàn bộ quá trình kiểm định hành vi. Do đó, đề tài sẽ tiến hành khảo sát có hệ thống các mô hình sinh dữ liệu học sâu tiên tiến chuyên biệt cho dữ liệu dạng bảng. Cụ thể, nghiên cứu tập trung đánh giá các đại diện đột phá thuộc họ Diffusion Model bao gồm ForestDiffusion, TabSyn và TabDDPM [3], đồng thời tiến hành đối sánh với các kiến trúc GAN tiêu biểu là CTGAN [4] (mô hình tối ưu hóa riêng cho cấu trúc dữ liệu bảng) và WGAN-GP (kiến trúc cải tiến với độ ổn định huấn luyện cao). Các mô hình này sẽ được phân tích toàn diện dựa trên bốn nhóm tiêu chí cốt lõi: độ trung thực của phân phối (Fidelity), độ bao phủ và đa dạng mẫu (Coverage & Diversity), khả năng kiểm soát nhãn điều kiện (Conditional Control), và chi phí tính toán (Resource & Latency). Phương pháp được chọn cuối cùng phải đảm bảo điểm cân bằng tốt nhất giữa độ chính xác mô phỏng và hiệu năng vận hành trong ngữ cảnh thời gian thực của vòng lặp FL‑IDS.
Xây dựng cơ chế chấm điểm đóng góp DT-Driven Performance Weighting (DT-PW): Đây là cơ chế để xử lý free‑rider, tức là những client gần như không học gì mà chỉ sao chép mô hình chung.
Cách đo đóng góp: Thay vì chỉ nhìn vào tham số mô hình, server đưa cả mô hình của client và mô hình chung vào Digital Twin, cho chúng dự đoán trên cùng một bộ dữ liệu thách thức rồi so sánh kết quả. Client thật sự huấn luyện trên dữ liệu riêng sẽ cho ra dự đoán khác so với mô hình chung. Free‑rider chỉ sao chép mô hình chung nên dự đoán gần như y hệt.
Cổng nỗ lực (Effort Gate): Dựa trên mức độ khác nhau trong dự đoán, hệ thống tự động đặt một ngưỡng:
Nếu dự đoán của client quá giống mô hình chung, client bị xem là free‑rider và điểm đóng góp bị đưa về không.
Nếu vượt qua ngưỡng này, client được chấm điểm đóng góp tỉ lệ với mức độ khác biệt trong dự đoán (tức là lượng tri thức mới mang lại).
3. Phương pháp và thực nghiệm
Nội dung 1: Khảo sát, phân tích các nghiên cứu liên quan và công nghệ nền tảng
Tổng hợp tài liệu về Federated Learning, Digital Twin, các hình thức tấn công poisoning/backdoor tiên tiến (LIE, Min‑Max, Min‑Sum, MPAF, Backdoor). Phân tích có hệ thống hạn chế của các phương pháp phòng thủ hiện có (LUP, ClipCluster, SignGuard, GeoMed, PoC, Krum, Median, Trimmed Mean) và các framework DT‑FL, blockchain‑FL gần đây để làm rõ ba khoảng trống nghiên cứu. Khảo sát các mô hình sinh dữ liệu dạng bảng (TabDDPM [3], TabSyn, ForestDiffusion, CTGAN [4], WGAN-GP) làm cơ sở lựa chọn bộ sinh dữ liệu thách thức cho Digital Twin.
Nội dung 2: Thiết kế và đề xuất hệ thống DT‑Guard
Mô hình hóa kiến trúc DT‑Guard theo dạng module, gồm: FL server, Digital Twin, bộ sinh dữ liệu thách thức (tích hợp các mô hình học sâu sinh mẫu dạng bảng), pipeline kiểm định hành vi bốn lớp (hiệu năng phát hiện xâm nhập, khả năng kháng backdoor, mức lệch tham số, độ ổn định qua các vòng), và Aggregator DT-PW (nhận mô hình, chạy Inference trên DT, tính toán Performance Score, tổng hợp trọng số). Xác định rõ luồng dữ liệu và giao tiếp giữa các module. Thiết kế cơ chế Effort Gate để phát hiện và loại bỏ free‑rider dựa trên mức độ khác biệt dự đoán giữa mô hình client và mô hình toàn cục.
Nội dung 3: Hiện thực hệ thống và thực nghiệm đánh giá
Cài đặt toàn bộ hệ thống bằng Python/PyTorch trên môi trường FL mô phỏng. Huấn luyện và đánh giá A/B Testing các mô hình sinh (Diffusion và GAN) để chọn bộ sinh challenge data tối ưu (Kịch bản 1). Khởi tạo mô phỏng FL với 20 clients trên dữ liệu CIC‑IoT‑2023 [5], cài đặt mô hình IoTAttackNet và 5 kịch bản tấn công. Chạy thực nghiệm so sánh DT-Guard với 9 phương pháp phòng thủ baseline (Kịch bản 2). Đánh giá tính công bằng đóng góp: so sánh DT-PW với FedAvg, Trust-Score (LUP/PoC) và Uniform (Kịch bản 3).
Nội dung 4: Phân tích kết quả, đánh giá tác động và hạn chế
Xử lý số liệu, trực quan hóa kết quả (bảng Accuracy/FPR/Detection Rate, đường cong hội tụ, biểu đồ phân bổ trọng số). Phân tích đánh đổi chi phí – lợi ích (Latency, CPU/RAM) giữa DT-PW và các phương pháp đối chứng. Đánh giá tác động của từng thành phần (ablation study): vai trò của bộ sinh dữ liệu, pipeline kiểm định bốn lớp, và Effort Gate. Nhận diện hạn chế và hướng phát triển. Viết bản thảo bài báo khoa học và hoàn thiện luận văn.
4. Thiết lập thực nghiệm
Thực nghiệm được chia thành 3 kịch bản chính nhằm tối ưu hóa từng thành phần, đánh giá toàn diện hệ thống và phân tích chuyên sâu:
Kịch bản 1: Đánh giá và tối ưu bộ sinh dữ liệu (A/B Testing)
Nhằm xác định mô hình sinh mẫu tối ưu nhất cho Digital Twin, đề tài đối sánh 5 kiến trúc thuộc 2 nhóm:
Nhóm Diffusion: TabDDPM (SOTA cho dữ liệu bảng), TabSyn (tối ưu luồng nhiễu dữ liệu hỗn hợp), và ForestDiffusion (tích hợp thuật toán dạng cây).
Nhóm GAN: CTGAN (chuyên biệt xử lý biến phân loại) và WGAN-GP (mô hình đối sánh - Baseline).
Kịch bản 2: Đánh giá hiệu năng phòng thủ của hệ thống DT-Guard
Dữ liệu: Bộ dữ liệu CIC‑IoT‑2023 [5]/ToN_IoT, phân bổ cho 20 client.
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
<bổ sung so sánh thực nghiệm tradeoff latency/consumption>
Các chỉ số đánh giá: Hệ thống chỉ số được chia làm 3 nhóm tương ứng với 3 kịch bản thực nghiệm:
Nhóm 1 - Chỉ số tối ưu bộ sinh dữ liệu:
Độ trung thực (Fidelity): Đo lường hiệu năng phân loại chéo qua chỉ số TSTR (Train on Synthetic, Test on Real), kết hợp đánh giá sự sai lệch phân phối bằng khoảng cách Wasserstein (cho biến liên tục) và Jensen-Shannon Distance (JSD - cho biến phân loại).
Độ bao phủ và đa dạng (Coverage & Diversity): Đánh giá mức độ ghi nhớ dữ liệu qua khoảng cách DCR (Distance to Closest Record) và hệ chỉ số PRDC (Precision, Recall, Density, Coverage) nhằm đảm bảo mô hình sinh được các mẫu tấn công đa dạng, tránh hiện tượng sập mode.
Kiểm soát điều kiện (Conditional Control): Đo lường độ chính xác nhãn giả định (Label Accuracy) thông qua việc kiểm chứng bằng một mô hình IDS chuẩn (Oracle).
Chi phí tính toán (Resource & Latency): So sánh thời gian huấn luyện (Training Time), độ trễ sinh mẫu (Generation Latency) và mức chiếm dụng CPU/RAM để đánh giá tính khả thi khi tích hợp vào vòng lặp FL.
Nhóm 2 - Chỉ số hiệu năng FL-IDS:
Độ chính xác (Accuracy) & Tỉ lệ lỗi (Error Rate): Hiệu năng phát hiện xâm nhập dưới mỗi kịch bản tấn công và mức suy giảm so với base.
Tỉ lệ phát hiện (Detection Rate) & FPR: Khả năng của Digital Twin nhận diện chính xác client độc hại và tỉ lệ loại bỏ nhầm client lành tính.
Nhóm 3 - Chỉ số đánh giá tính công bằng và đóng góp:
Trọng số trung bình theo vai trò (Average Weight by Role): Đo lường và đối sánh mức trọng số trung bình mà các chiến lược gán cho từng nhóm client (Free-Rider, Normal). Đây là chỉ số cốt lõi để minh chứng khả năng nhận diện hành vi lười biếng của DT-PW.
Đường cong hội tụ (Convergence Curve): Theo dõi sự biến thiên của độ chính xác (Accuracy) qua từng vòng lặp FL của các chiến lược đối chứng, qua đó khẳng định DT-PW giúp mô hình chung hội tụ nhanh và duy trì độ ổn định tốt hơn.
Biểu đồ phân bổ trọng số (Weight Distribution): Trực quan hóa sự phân bổ trọng số chi tiết của từng client dưới các phương pháp tiếp cận khác nhau (DT-PW, Shapley, Trust-Score, Uniform) nhằm làm rõ năng lực phân biệt rạch ròi giữa đóng góp thực chất và đóng góp rỗng.
Chi phí tính toán và Tài nguyên (Latency & Resource Consumption): Đo lường độ trễ tổng hợp (Aggregation Latency) và mức chiếm dụng phần cứng (CPU/RAM) trong quá trình chấm điểm. Chỉ số này dùng để trực quan hóa bài toán đánh đổi giữa phần chi phí tăng thêm của DT-PW so với các phương pháp baseline (FedAvg, LUP/PoC, Uniform) và lợi ích công bằng thu lại được.
5. Kết quả dự kiến
Hệ thống hóa thành công khung phòng thủ DT‑Guard: Đề xuất và xây dựng kiến trúc DT-Guard cho FL-IDS. Kết quả này lấp đầy khoảng trống của các phương pháp thụ động bằng cách chuyển dịch sang kiểm chứng chủ động thông qua Digital Twin, phân biệt rõ ràng giữa sai lệch do Non-IID tự nhiên và hành vi phá hoại.
Thiết lập cơ chế tổng hợp tối ưu DT-PW: Hoàn thiện thuật toán định lượng đóng góp dựa trên hiệu năng thực tế. Cơ chế này loại bỏ hoàn toàn tác động của các Free-riders và ưu tiên các Client ưu tú, từ đó đẩy nhanh tốc độ hội tụ.
Chứng minh hiệu năng vượt trội qua thực nghiệm: Bảng phân tích khẳng định sức chống chịu của DT-Guard trước 5 kịch bản tấn công (Backdoor, LIE, Min‑Max, Min‑Sum, MPAF). Duy trì độ chính xác cao, giảm thiểu tỉ lệ lỗi và giữ FPR ở mức thấp nhất so với 9 phương pháp baseline hiện có ngay cả trong điều kiện Non-IID cực đoan.
Hoàn thiện các module tối ưu hóa chuyên sâu: Đảm bảo tính khả thi của hệ thống bao gồm cơ chế tổng hợp dung hợp giữa Performance-Score và Trust-Score; hoàn tất đánh giá đối sánh chọn ra mô hình sinh dữ liệu dạng bảng tốt nhất cho môi trường Digital Twin.
Sản phẩm khoa học và tài liệu: Báo cáo luận văn hoàn chỉnh; Mã nguồn (source code) phục vụ tái lập; Ít nhất một bản thảo bài báo khoa học.
6. Tài liệu tham khảo
[1] Issa et al. (2025), "DT‑BFL: Digital Twins for Blockchain‑enabled Federated Learning in Internet of Things networks", Ad Hoc Networks, Elsevier.
[2] Zhang et al. (2025), "Adaptive Asynchronous Federated Learning for Digital Twin Driven Smart Grid", IEEE Transactions on Smart Grid, Vol.16, No.5.
[3] Kotelnikov et al. (2023), "TabDDPM: Modelling tabular data with diffusion models", Proceedings of the 40th International Conference on Machine Learning (ICML 2023).
[4] Xu et al. (2019), "Modeling Tabular data using Conditional GAN", Advances in Neural Information Processing Systems (NeurIPS 2019).
[5] Neto et al. (2023), "CICIoT2023: A Real-Time Dataset and Benchmark for Large-Scale Attacks in IoT Environment", Sensors.
[6] Baruch et al. (2019), "A Little Is Enough: Circumventing Defenses for Distributed Learning", Advances in Neural Information Processing Systems (NeurIPS 2019).
[7] Shejwalkar and Houmansadr (2021), "Manipulating the Byzantine: Optimizing Model Poisoning Attacks and Defenses for Federated Learning", Network and Distributed System Security Symposium (NDSS 2021).
[8] Xu et al. (2022), "SignGuard: Byzantine-tolerant Federated Learning through Collaborative Malicious Gradient Filtering", IEEE 42nd International Conference on Distributed Computing Systems (ICDCS 2022).
[9] Zeng et al. (2024), "ClipCluster: A Defense against Byzantine Attacks in Federated Learning", IEEE Transactions on Information Forensics and Security, Vol.19.
[10] McMahan et al. (2017), "Communication-Efficient Learning of Deep Networks from Decentralized Data", Proceedings of the 20th International Conference on Artificial Intelligence and Statistics (AISTATS 2017).
[11] Yin et al. (2018), "Byzantine-Robust Distributed Learning: Towards Optimal Statistical Rates", Proceedings of the 35th International Conference on Machine Learning (ICML 2018).
[12] Pillutla et al. (2022), "Robust Aggregation for Federated Learning", IEEE Transactions on Signal Processing, Vol.70.
[13] Blanchard et al. (2017), "Machine Learning with Adversaries: Byzantine Tolerant Gradient Descent", Advances in Neural Information Processing Systems (NeurIPS 2017).


Nội dung công việc chi tiết

Nội dung 1 – Khảo sát, phân tích nghiên cứu liên quan và công nghệ nền tảng
- Rà soát tài liệu về FL, Digital Twin, các phương pháp phòng thủ và tấn công poisoning.
- Phân tích hạn chế của các phương pháp hiện có, làm rõ ba khoảng trống nghiên cứu.
- Khảo sát các mô hình sinh dữ liệu dạng bảng (TabDDPM, TabSyn, ForestDiffusion, CTGAN, WGAN-GP).

Nội dung 2 – Thiết kế và đề xuất hệ thống DT‑Guard
- Mô hình hóa kiến trúc DT‑Guard theo dạng module (FL server, Digital Twin, bộ sinh dữ liệu, pipeline kiểm định bốn lớp, Aggregator DT-PW).
- Thiết kế cơ chế Effort Gate và thuật toán DT-PW.
- Xác định luồng dữ liệu và giao tiếp giữa các module.

Nội dung 3 – Hiện thực hệ thống và thực nghiệm đánh giá
- Cài đặt hệ thống bằng Python/PyTorch trên môi trường FL mô phỏng.
- Đánh giá A/B Testing bộ sinh dữ liệu để chọn challenge data tối ưu (Kịch bản 1).
- Khởi tạo FL với 20 clients trên CIC‑IoT‑2023, cài đặt 5 kịch bản tấn công (Kịch bản 2).
- So sánh DT-PW với FedAvg, Trust-Score, Uniform (Kịch bản 3).

Nội dung 4 – Phân tích kết quả, đánh giá tác động và hạn chế
- Xử lý số liệu, trực quan hóa kết quả (bảng, đường cong hội tụ, biểu đồ trọng số).
- Phân tích đánh đổi chi phí – lợi ích (Latency, CPU/RAM).
- Nhận diện hạn chế và hướng phát triển.
- Viết bản thảo bài báo khoa học và hoàn thiện luận văn.
