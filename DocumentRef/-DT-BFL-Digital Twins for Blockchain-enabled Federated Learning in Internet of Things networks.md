

Contents lists available at ScienceDirect
## Ad Hoc Networks
journal homepage: www.elsevier.com/locate/adhoc

DT-BFL: Digital Twins for Blockchain-enabled Federated Learning in Internet
of Things networks
## Wael Issa
a,
## ∗
## , Nour Moustafa
a
## , Benjamin Turnbull
a
, Kim-KwangRaymond Choo
b
a
School of Systems & Computing , University of New South Wales Canberra, Northcott Drive, Campbell, 2612, ACT, Australia
b
Department of Information Systems and Cyber Security, University of Texas at San Antonio, San Antonio, TX 78249, USA
## A R T I C L E   I N F O
## Keywords:
Digital Twins (DT)
Federated Learning (FL)
Internet of Things (IoT)
## Blockchain
Poisoning attacks

## A B S T R A C T
Sixth-generation (6G) wireless networks enable faster, smarter, and more connected Internet of Things (IoT)
systems, which in turn support edge intelligence and real-time decision-making. Federated learning (FL)
supports this shift by allowing devices to collaboratively train models without sharing raw data, which helps to
protect user privacy. There are, however, potential security challenges in FL deployments. For example, security
challenges such as poisoning attacks and Byzantine clients can compromise the training process and degrade
the accuracy and reliability of the global model. Although existing methods can detect malicious updates,
many advanced attacks still bypass statistical defenses relying on metrics such as median and distance. In other
words, developing an FL system that ensures both reliable decision-making and privacy and security guarantees
in IoT networks remains a significant challenge. This study introduces a Digital Twin-driven Blockchain-
enabled Federated Learning (DT-BFL) framework designed for IoT networks. The framework creates a digital
representation of the IoT environment to support secure and decentralized edge intelligence using blockchain
and federated learning technologies. DT-BFL is built to detect and filter out potentially poisoned model updates
from malicious participants. This is achieved through a new smart contract-enabled decentralized aggregation
method called Local Updates Purify (LUP). LUP uses a two-stage filtering process: First, it applies Median
Absolute Deviation (MAD) to initially remove outliers, then uses statistical features and clustering to separate
honest from malicious updates before aggregating the global model. It also assigns a Trust Score (TS) to
each participant based on how much their updates differ from the global model and then uses a genuine
criterion to select honest clients by evaluating trust scores, update similarity, and deviation from the global
model. Experimental results show that DT-BFL effectively defends against various poisoning attacks on datasets
like MNIST, ToN-IoT, and CIFAR-10 using models such as CNN, MLP, ResNet, and DenseNet, and maintains
high accuracy even when 50% of the clients are malicious. Using a permissioned blockchain further secures
the system by enabling aggregation of the decentralized model and authentication of clients through smart
contracts. The source code is available on https://github.com/UNSW-Canberra-2023/LUP.
## 1. Introduction
To fully realize edge intelligence, sixth-generation-based Internet
of Things (6G-IoT) networks rely on intelligent devices such as smart-
phones, vehicles, sensors, actuators, and semi-autonomous robots [1].
The rapid evolution of IoT networks has led to edge intelligence-based
applications emerging across diverse industries, including smart health-
care, smart homes, smart grids, and agriculture. These applications are
characterized by a strong need for efficiency, security, and privacy,
introducing new challenges for edge intelligence. Digital Twin (DT)
technology [2,3] is emerging as an innovation within 6G-IoT networks,
offering the ability to connect physical system objects with their digital
## ∗
Corresponding author.
E-mail addresses: w.issa@unsw.edu.au (W. Issa), nour.moustafa@unsw.edu.au (N. Moustafa), benjamin.turnbull@unsw.edu.au (B. Turnbull),
raymond.choo@fulbrightmail.org (K.-K.R. Choo).
counterparts. This connection enables real-time monitoring and predic-
tive capabilities for physical entities. By harnessing the digital twin
technology, 6G-IoT networks would effectively link between physical
systems and the digital realm, facilitating robust edge intelligence in
IoT applications. According to Gartner, a significant 62% of developed
enterprise-based IoT projects rely on digital twin technology [4].
Existing digital twin approaches encounter communication burdens
as they transmit data from physical objects to a centralized server for
twin mapping [5]. Specifically, traditional centralized machine learning
(ML) schemes typically require data generated on user devices to be
transmitted to a central server for processing. These schemes introduce
https://doi.org/10.1016/j.adhoc.2025.103934
Received 1 February 2025; Received in revised form 16 April 2025; Accepted 22 May 2025
## Ad Hoc Networks 178 (2025) 103934
Available online 7 June 2025
1570-8705/© 2025 The Authors. Published by Elsevier B.V. This is an open access article under the CC BY license (
http://creativecommons.org/licenses/by/4.0/ ).

W. Issa et al.
considerable communication overhead and give rise to substantial se-
curity and privacy challenges [5]. Moreover, transmitting vast amounts
of data in untrusted and non-transparent 6G-IoT environments poses
security risks for users. Additionally, malicious physical devices would
propagate false data or low-quality models, undermining the integrity
of digital twin-edge intelligence.
For instance, Zhang et al. [6] investigated the integration of digital
twinning with multi-access edge computing (MEC) in IIoT. In this
scenario, a DT server is established at the edge layer to serve as a
digital replica of the MEC server. They reported that integrating the
digital twin can enhance the efficiency of offloading decision-making,
leading to improved computing performance compared to MEC servers
without digital twin integration. However, centralized digital twins face
significant limitations, including high latency, data bottlenecks, and
a single point of failure, which hinder real-time responsiveness and
system reliability. Additionally, they raise concerns about scalability,
privacy, and security due to the concentration of sensitive data in a
single location [7].
Federated Learning (FL) has been explored as a potential solution
to address these challenges. In an FL framework, devices, including IoT
devices, can train machine learning models locally and then send their
updates to a central server for global model aggregation [8]. However,
traditional FL schemes do not guarantee the security or quality of local
updates and often lack trust among participants. As a result, malicious
participants may upload fake or poisoned model parameters, which can
harm the training process and reduce the accuracy of the global model.
Additionally, relying on a central server for aggregation introduces a
single point of failure and increases vulnerability to attacks [8].
To address these issues, many studies have focused on mitigating
the impact of poisoning attacks in FL. Some approaches use statistical
methods to detect poisoned updates by treating them as outliers. Oth-
ers [9,10] assume the availability of a labeled, representative dataset
on the server to evaluate the accuracy of local updates and distinguish
between honest and malicious contributions. However, this assumption
is often unrealistic due to privacy concerns and data availability limita-
tions. Another group of approaches uses clustering techniques [11,12],
based on the assumption that honest updates outnumber malicious
ones. Despite these efforts, recent research [13,14] shows that sta-
tistical aggregation methods remain vulnerable to carefully designed
poisoning attacks in FL.
While FL offers a privacy-preserving alternative to traditional cen-
tralized machine learning, as a paradigm, security is still a necessarily
active area of research. This need to improve security is especially true
for large-scale, distributed systems such as IoT. In such systems, many
devices may participate in training, including potentially untrustworthy
ones, which increases the need for stronger security measures [8]. It
is therefore important to design an FL scheme that can handle the
decentralized nature of IoT environments. Such a scheme would reduce
the risk of single points of failure, secure the exchange of local updates,
and limit the impact of poisoning attacks from malicious clients. Several
studies have explored the integration of FL with digital twins (DTs).
For example, Praharaj et al. [15] introduced a hierarchical federated
transfer learning framework using digital twins to enable privacy-aware
collaborative learning for anomaly detection in smart farming. In this
setup, anomaly detection models are trained locally on data collected
by edge digital twins, and the global model is aggregated at both the
edge and cloud servers.
The key challenge of this field is how to design a secure and reliable
FL system for distributed IoT environments [5,8]. Blockchain [16,17]
offers a promising solution by acting as a decentralized ledger that
eliminates the need for a central authority. It provides a tamper-
resistant storage system supported by consensus protocols and smart
contracts. These smart contracts help validate and secure data transac-
tions, while consensus mechanisms ensure that the information stored
in the ledger is accurate and trusted. This structure helps build trust
among FL participants by monitoring the learning process and detecting
corrupted model updates or malicious clients [18]. Several studies have
explored the combination of blockchain, FL, and digital twins in IoT
systems. For example, Qu et al. [19] proposed BAFL-DT, a blockchain-
based asynchronous FL model that uses digital twins to offer edge AI
services. Lu et al. [20] introduced DITEN, a blockchain-supported FL
framework. However, these approaches still rely on training models on
limited-resource IoT devices and do not include a strong global model
aggregation method.
This study presents a new Digital Twin-driven Blockchain-enabled
federated learning (DT-BFL) framework in IoT networks. The proposed
framework primarily links physical IoT devices to facilitate secure and
decentralized edge intelligence through the combined utilization of
Blockchain and federated learning. Furthermore, it incorporates a de-
centralized smart contract-enabled aggregation algorithm named LUP
to filter and discard potentially poisoned model updates from malicious
participants, thereby bolstering the overall integrity of the federated
learning process. LUP is based on a two-stage filtering process that
combines MAD and hierarchical clustering. Unlike other approaches
in the literature, LUP introduces a genuine criterion to identify the
honest cluster without relying on the assumption that honest clients
are in the majority. The genuine criterion evaluates participants based
on their TS, local model deviations from the global model, and kurtosis.
Moreover, it updates each client’s TS based on the degree of deviation
from the most recent global model update.
Specifically, DT-BFL offers several benefits for 6G-enabled IoT net-
works. First, it enables digital twin-edge intelligence, allowing physical
devices to exchange data with their corresponding edge digital twins,
which supports collaborative learning secured by blockchain and LUP.
Second, it removes the need for a central authority by using a per-
missioned blockchain to ensure trust, and to securely exchange and
store local model updates from authenticated participants. Third, it
supports robust decentralized aggregation by executing LUP through
smart contracts and validating the results via consensus among edge
servers. Additionally, the resulting global model is stored in the Inter-
Planetary File System (IPFS)—an off-chain storage solution—allowing
participants to download it and begin the next federated learning
round. The framework also addresses constraints related to computa-
tional resources and real-time data exchange through the use of edge
digital twins. In summary, the main contributions of this work are as
follows:
•We propose a novel framework, called DT-BFL, that integrates
decentralized edge intelligence, digital twins, federated learning,
and permissioned blockchain to enhance the efficiency, security,
and reliability of edge intelligence in IoT networks. Specifically,
DT-BFL ensures trustworthy and secure federated learning among
untrusted participants through a permissioned blockchain, mit-
igating the single point of failure of centralized architectures.
Moreover, it employs smart contract-enabled aggregation to au-
tomatically filter and exclude poisoned model updates, guaran-
teeing the integrity of the global model against various poisoning
attacks.
•We propose LUP, a robust aggregation scheme for filtering mali-
cious updates in federated learning. LUP utilizes two filters: one
based on MAD of update norms and another employing statistical
features and AHC to differentiate between honest and malicious
updates. It also incorporates a genuine criterion to identify hon-
est clients by evaluating their trust scores, and model update
similarity to the global model. In addition, it introduces the
Degree of Deviation (DoD) concept to assign trust scores (TS) to
participants. LUP’s execution and validation occur decentralized
via smart contracts and permissioned blockchain peers.
•We conduct extensive experiments to evaluate the performance
of the DT-BFL framework and the robustness of LUP under di-
verse adversarial scenarios. Our results, validated across multiple
datasets (e.g., MNIST, ToN-IoT, CIFAR-10) and model architec-
tures (e.g., CNN, MLP, ResNet, DenseNet), demonstrate that LUP
## Ad Hoc Networks 178 (2025) 103934
## 2

W. Issa et al.
consistently outperforms existing defense schemes, maintaining
high model accuracy even when up to 50% of participants are
malicious. Additionally, we benchmark blockchain throughput
and latency.
The remainder of the paper is structured as follows. Section 2
provides background information on blockchain, poisoning attacks, and
digital twins. Section 3 discusses related works and their limitations.
Section 4 introduces the design details of DT-BFL. Section 5 describes
the LUP algorithm and the simulation setup of DT-BFL. Sections 6 and
7 present the experimental findings and the conclusion, respectively.
## 2. Background
2.1. Edge intelligence
In the domain of 6G-IoT edge intelligence, AI models are relocated
to be trained directly on IoT devices and subsequently aggregated by
edge servers. This eliminates the need to transmit data or models to
the cloud tier as edge devices increase computational capacity. Edge
intelligence is envisaged as the synergistic utilization of AI, advanced
communication techniques, and the computational resources available
at the edge [1]. Edge intelligence aims to decentralize computing
intelligence across the network by relocating AI models and predic-
tive analytics services closer to the data source. This approach is
advantageous as it eliminates the need to transmit data to the cloud
for analysis, ensuring intelligence is in proximity to the data genera-
tor [21]. According to Lu et al. [3], adopting emerging technologies
such as digital twins and 6G networks has sped up the implementation
of edge intelligence in the IoT domain. However, issues like unreliable
communication, data security, privacy, and the absence of trust among
clients impede the effectiveness of FL applications in IoT.
2.2. Digital twinning
The digital twin (DT) emerges as a critical foundational technology
for smart IoT systems, seamlessly integrating cutting-edge information
technologies like AI and blockchain. Thus, the digital twin duplicates
the whole lifecycle of physical things and systems by combining phys-
ical models with historical data. Furthermore, it can record, monitor,
and forecast dangers via bidirectional interactive communication be-
tween physical and virtual domains [22]. DT has been utilized in
cybersecurity to create a simplified or offline digital replica of IoT
systems. This virtual emulation is a valuable tool for simulating cy-
berattacks and exploits, detecting vulnerabilities, and preemptively
identifying potential threats from external adversaries. This specialized
instance of a digital twin is called a cyber twin. It can also combine with
cutting-edge technologies such as AI, edge computing, operational tech-
nologies (for example, enhanced controllers), and telecommunication
technologies (for example, 6G networks) [23].
Several research studies have investigated the development of DT
for IoT systems. For example, Koroniotis et al. [23] highlighted the
growing prevalence of IIoT systems, particularly within environments
such as smart airports, driven by advanced devices and wireless con-
nectivity. Despite offering benefits such as improved communication
and efficiency, IIoT also introduces vulnerabilities, necessitating robust
cybersecurity measures. They introduce SAirIIoT, a new testbed for
secure cybertwins in smart airports, focusing on IIoT security, enabling
remote experimentation with adversarial and defense scenarios in IIoT
environments. However, this study has not explored the integration
of distributed edge intelligence via federated learning and blockchain
technology to promote data security and privacy.
## 2.3. Blockchain
Blockchain is a decentralized, transparent, and tamper-proof ledger
system with key features including decentralization, traceability, trust,
and immutability. These qualities make it a valuable addition to 6G-
enabled IoT and federated learning at the edge, allowing for improved
security, privacy, and reliability. Blockchains are generally catego-
rized as either public (permissionless) or private (permissioned). Public
blockchains, such as Bitcoin and Ethereum, allow anyone to participate
and validate transactions. In contrast, private blockchains, such as
Hyperledger Fabric, restrict access to approved participants who must
be verified. [24].
Fully decentralizing FL presents a viable strategy for enhancing the
security and reliability of edge intelligence systems. To achieve this,
blockchain can potentially be leveraged to validate the computational
process of edge intelligence, identify poisoned models, securely store
local models, and facilitate decentralized aggregation schemes through
smart contracts. Allowing blockchain peers to register and authenticate
FL clients enables a fully decentralized FL without needing a central en-
tity for the global model aggregation. Moreover, blockchain can enable
the secure aggregation and validation of the global model by filtering
out poisoned models and facilitating consensus among blockchain peers
regarding the correctness of the computed global model. Additionally,
employing blockchain-based cryptography techniques can obscure the
data flow among blockchain peers, mitigating threats related to data
modification [1,25].
2.4. Poisoning attacks
Essentially, FL comes with the principles of ensuring participants’
data privacy and security. However, the inherent risks from adversarial
threats make it susceptible to poisoning attacks that aim to compromise
the integrity of the global model during the FL training. Poisoning
attacks come in targeted or untargeted forms. In untargeted poisoning
attacks, malicious clients subtly manipulate their local data or trained
models to undermine the global model integrity, such as injecting
crafted spam messages into a spam classifier to misclassify legitimate
emails. Conversely, targeted poisoning attacks are more intentional,
focusing on manipulating the model’s behavior on specific inputs, like
altering stop signs in an image recognition system to be misclassified as
speed limit signs, potentially leading to dangerous road scenarios [26,
## 27].
- Related work
In this section, we will discuss a sample of related work, high-
lighting their motivations, contributions, and limitations that inspire
our proposed framework. Some of these works focus on integrating
blockchain with federated learning to enhance its security. In contrast,
others leverage digital twin in conjunction with blockchain and feder-
ated learning to address resource constraints of IoT devices, aiming to
provide real-time predictions and analysis and empower IoT devices to
control their environments intelligently.
Qu et al. [19] introduced a blockchain-based asynchronous feder-
ated learning service model called BAFL-DT, which leverages digital
twins to enable edge AI as a service in IoT systems. In BAFL-DT, digital
twins are deployed on the cloud to replicate IoT devices, enabling local
models to be trained on the devices. In addition, the digital twins han-
dle model aggregation and blockchain ledger. BAFL-DT incorporates
Proof-of-Federalism (PoFe) as a consensus protocol and utilizes the
Markov decision process (MDP) to select the local model parameters
for global model aggregation. To summarize, this work emphasized
the importance of considering the privacy of local model updates and
detecting poisoned models before aggregating them into the global
model, highlighting this for future research.
## Ad Hoc Networks 178 (2025) 103934
## 3

W. Issa et al.
## Table 1
Comparison of DT-BFL with related frameworks (✓ = Fully supported, ∼ = Partially supported, × = Not supported).
FrameworkDT SupportBlockchainFL SupportRobust AggregationStorageConsensusSecurity
EcoEdgeTwin [28]✓××××××
## CODECO [29]×✓✓××∼×
## BAFL-DT [19]✓✓✓∼×✓∼
## DITEN [20]✓✓✓∼×✓∼
## B-FL [30]×✓✓∼××✓
## DT-BFL✓✓✓✓✓✓✓
To enhance the security of IoT edge computing, Lu et al. [20]
proposed a blockchain-enabled federated learning architecture named
the Digital Twin-enabled Edge Networks (DITEN). This architecture
trains the local model on the device while aggregating them on edge
digital twins. Moreover, the blockchain provides transparent storage
of local models and consensus on the edge servers. Additionally, it
employs a deep reinforcement learning module for user selection and
resource management. However, this architecture does not address the
verification of local models received from the local devices and the
filtering of false ones.
There are also studies focused on developing IoT digital twin-based
networks that are managed and secured by blockchain. For example,
Jiang et al. [31] proposed a framework that integrates digital twins,
directed acyclic graph (DAG) consortium blockchain, and federated
learning. In this framework, local devices send their data to the nearest
access point (AP), which can train a cooperative model and send it
to digital twins on the edge servers for aggregation, verification, and
secure storage on the blockchain ledger. Moreover, this framework
includes a double auction-based joint cooperative federated learning
approach and a local model update verification scheme to incentivize
participants to contribute to federated learning.
Similarly, Lu et al. [3] introduced digital twin wireless networks
(DTWN), leveraging blockchain-enabled federated learning to enhance
security and data privacy during global model training. Furthermore,
a reinforcement learning model is employed to optimize resource allo-
cation. Also, a Clustered Federated Learning (CFL) framework, incor-
porating Intelligent Selection and Computation Offloading (CISCO-FL),
is introduced by Abdulrahman et al. [2] based on digital twins to
address the challenges posed by resource-constrained IoT devices. This
framework enables clients with adequate computational resources to
assist those with limited resources, aiming to optimize communication
and computational resources.
Intending to enhance data privacy, filter poisoned model updates,
and reduce energy consumption, Yang et al. [30] proposed a de-
centralized blockchain-enabled Federated Learning (B-FL). In B-FL,
permissioned blockchain and FL are integrated to facilitate trusted
learning for IoT devices while mitigating the impact of poisoning
attacks using a multi-Krum algorithm. However, the multi-Krum [32]
algorithm has several limitations and does not effectively filter out
advanced poisoning attacks such as Min-Max and Min-Sum, particularly
when the number of Byzantine clients approaches or exceeds 50% of
FL clients [13]. Also of note, a dynamic digital twin for aerial-assisted
Internet of Vehicles (IoV) was created by Sun et al. [33]. This research
proposes an incentive mechanism rooted in the Stackelberg game the-
ory to encourage client collaboration in model training, as well as to
optimize resource allocation and power consumption. However, this
study does not address challenges related to security and data privacy
when exchanging local model updates in IoV.
Lv et al. [34] conducted a study on the integration of Blockchain,
federated learning, and Digital Twin, proposing a secure distributed
data sharing (DDS) framework to bolster the security and reliability of
data protection in IoT. They also introduced a methodology for filtering
poisoning attacks; however, they observed vulnerabilities when the
number of byzantine clients exceeded 10%. Thus, they emphasized
the ongoing challenge of developing a robust filtration approach to
counteract poisoning attacks. Tang et al. [35] explored the potential
of integrating DT technology with FL to enhance real-time collision
warning systems. Their study involved the development of DT-enabled
collision warning frameworks consisting of a physical network, digital
twin, and application layers. Additionally, they introduced an innova-
tive parameter adjustment algorithm based on asynchronous advantage
actor-critic (A3C) to minimize training delays and provide timely pre-
dictions. However, the study did not address measures for ensuring the
security and privacy of model updates during the federated learning
process.
EcoEdgeTwin [28] by Karobi et al. is the result of research that
introduces a Digital Twin-driven edge architecture tailored for 6G net-
works. EcoEdgeTwin aims to optimize service delivery through proac-
tive task offloading and adaptive resource allocation. Leveraging deep
reinforcement learning (A2C) and a digital twin discrepancy factor,
the framework reduces latency and improves energy efficiency under
dynamic edge environments. However, EcoEdgeTwin primarily targets
resource optimization and does not explicitly address the security, trust-
worthiness, or robustness of federated model updates. Similarly, the
CODECO framework [29], proposed by Sofia et al. presents a cognitive,
decentralized container orchestration system for the Edge-Cloud contin-
uum, utilizing AI-driven resource scheduling and metadata-based opti-
mization across distributed infrastructures. While CODECO enhances
adaptive workload placement, it primarily focuses on infrastructure-
level orchestration and lacks mechanisms for secure model aggregation,
trust-aware federated learning, or blockchain-based consensus.
The comparison in Table  1 shows that DT-BFL is the comprehensive
framework, uniquely supporting edge-based Digital Twins, trust-aware
federated learning, robust aggregation (MAD, AHC, DoD), and decen-
tralized model storage via IPFS. While EcoEdgeTwin and CODECO
focus on service optimization and orchestration, they lack secure aggre-
gation and blockchain consensus. BAFL-DT and DITEN support Digital
Twins and blockchain but offer only basic or partial security and
aggregation features. B-FL includes Multi-Krum for robustness but lacks
decentralized storage and trust mechanisms.
In summary, the existing literature still faces several limitations.
These include the need for a robust approach to filter and mitigate
the impact of poisoning attacks while ensuring the performance of the
global model, particularly when the number of adversaries approaches
or exceeds half of the FL clients. Additionally, there is a critical need to
enable fully decentralized FL by leveraging smart contracts for secure
global model aggregation and utilizing permissioned blockchains for
storing local model updates and managing access control for FL clients.
Furthermore, permissioned blockchain networks can facilitate the se-
cure exchange of local model updates through the use of public and
private keys. Basically, integrating edge digital twins can address chal-
lenges related to resource constraints in IoT devices by interacting with
physical devices, collecting data, training local models, and providing
predictive analytics for intelligent risk management and control of the
surrounding environment.
- Proposed framework: DT-BFL
The proposed Digital Twin-driven Blockchain-enabled Federated
Learning (DT-BFL) framework comprises the IoT devices and edge
layers, as shown in Fig.  1. The IoT devices layer encompasses IoT appli-
ances, actuators, cameras, and sensors, which monitor the surrounding
environment and collect data. Recognizing the limited computational
resources of IoT devices, DT-BFL creates an edge digital twin to mirror
## Ad Hoc Networks 178 (2025) 103934
## 4

W. Issa et al.
them and gather real-time data for collaborative FL model training. The
edge layer, on the other hand, consists of three components. Firstly, the
edge digital twin oversees monitoring, control, and data reception from
the IoT devices. Secondly, the ordering edge server, a pivotal element of
the permissioned blockchain network, comprises multiple edge servers
for mutual backup. Its primary function is to receive client transactions,
validate them, order them into a block, and transmit them to the
third component: the edge blockchain network. This network involves
multiple edge servers responsible for block validation and addition to
the blockchain ledger.
In DT-BFL, the global model aggregation is conducted securely and
decentralized using smart contracts, which are lines of code deployed
on the validator edge servers in an immutable and trackable manner.
Once a block of local model updates is generated, the secure model
aggregation smart contract is triggered on all validator edge servers
to calculate the global model securely. Subsequently, the correctness
and integrity of the global model are validated using the PBFT (Prac-
tical Byzantine Fault Tolerance) consensus protocol. Once the edge
validators reach a consensus on the calculated global model, they save
it in the InterPlanetary File System (IPFS) and allow participants to
download it to initiate a new global round.
Therefore, the consensus protocol is essential in the blockchain
ecosystem, ensuring consistency and security within the decentralized
blockchain ledger. We utilize the PBFT, primarily designed for permis-
sioned blockchains, to fulfill consensus as long as fewer than one-third
of the edge servers in the network are faulty or compromised. PBFT is
known for its effectiveness in achieving consensus and for consuming
less electrical energy than Proof of Work (PoW) protocols. Specifi-
cally, the training process of the collaborative global model in DT-BFL
comprises six steps that will be executed in each FL round. These
steps are required to guarantee the integrity and trustworthiness of the
global model aggregation, thereby mitigating single points of failure
and thwarting potential poisoning attacks. Moreover, the systematic
flow of DT-BFL including LUP is depicted in Algorithms 1 and 2. These
steps are :
Step 1 - Digital Twinning:  The first step involves the creation of a
DT virtual replica for every IoT device, effectively mirroring its physical
counterpart. Edge servers within the DT-BFL framework manage and
maintain these digital twins. As part of this setup, each entity within
the digital twin ecosystem generates a private and corresponding public
key for registration purposes. The public key serves as the unique iden-
tity for each entity, facilitating secure interactions within the system.
When a connection is established between the DT and IoT devices, the
IoT devices are continuously synchronized with the nearest hive using
IoT data and states. This synchronization ensures that the digital twin
remains updated with real-time information and reflects the current
state of its physical counterpart. Once each entity of the DT receives
and collects local data from its corresponding physical IoT device, it
initiates interaction with the blockchain network, thereby commencing
a secure FL process.
Step 2 - DT Local Training: To enable DT entities to interact with
the permissioned blockchain network, they must first register via a
client registration smart contract. Subsequently, a smart authentica-
tion contract can validate their identities when they engage with the
blockchain network. Once registered, each DT entity can interact with
the permissioned blockchain network, facilitating the direct download
of the initial global model from IPFS. Consequently, each DT entity
trains the local model using its local data through stochastic gradient
descent.
Step 3 - Upload Local Updates:  When completing the local model
training, each DT entity uploads the local model to the ordering service
as a transaction. It is essential to note that digital signatures, a crypto-
graphic technique, are utilized to ensure the validity and integrity of
the transaction, guaranteeing that the transaction data remains untam-
pered with by unauthorized parties. Upon receiving the local model
updates, the ordering service incorporates them and arranges them
Fig. 1. System Model for DT-BFL.
within the current block. Once the ordering service accumulates enough
local updates from the participants or reaches the block generation
time, a new block is generated and broadcast to the blockchain peers
for validation.
Step 4 - Block Validation:  Upon the ordering service broadcasting
the block to the blockchain peers (edge servers), they begin verifying
the digital signatures of the transactions within the new block to as-
certain their validity. Following this verification step, each peer stores
the new block in its local ledger for further reference and consistency
across the network.
Step 5 - Consensus on Local Updates:  Once all peers have com-
pleted the block verification, the PBFT consensus protocol is invoked to
ensure that most of the peers (edge servers) have verified and acknowl-
edged the validity of the new block. Once consensus is achieved, the
new block is deemed valid, and all peers notify the ordering service
of its acceptance and storage within the blockchain, preparing for
subsequent blocks. The new block is linked to the blockchain ledger
upon reaching a consensus (See Box  I)
Step 6 - Global Model Aggregation: After confirming local model
updates in the new block and linking the block to the ledger of all peers,
each peer initiates a secure aggregation process using a smart contract.
This process aggregates the local updates into the global model using
the LUP algorithm, which filters out malicious updates and retains the
honest ones for aggregation. All peers execute the LUP algorithm at
this stage and achieve consensus on the calculated global model. Once
## Ad Hoc Networks 178 (2025) 103934
## 5

W. Issa et al.
Genuine_Criterion=
## ⎧
## ⎪
## ⎨
## ⎪
## ⎩
Cluster 2 is genuine,if TS_2≥TS_1 and grad_sim_2>grad_sim_1 and (kurt_2>kurt_1 or dev_2<dev_1)
Cluster 2 is genuine,if TS_2≥TS_1 and grad_sim_2>grad_sim_1 and dev_2<dev_1
Cluster 1 is genuine,otherwise
## (1)
## Box I.
Algorithm 1 DT-BFL Workflow
Input:  learning rate 휂←10
## −1
, batch size 퐿, number of communication
rounds 푅, number of local epochs 퐸, Register digital twins {퐷푇}
## 푀
## 푚=1
as clients in the blockchain network.
Output:  Trained global model: 푊
## 푔
## ——————– Edge Blockchain Network —————–
- Initialize: trust score for the clients: 푇 푆←[{0}
## 푀
## 푚=1
## ]
- Initialize: the initial global model parameters 푊
## 0
## 푔
- Send: the initial global model parameters 푊
## 0
## 푔
to the clients
while 푟≤푅 do
- Receive: the endorsed local model updated from the clients
- Stacks: the local model updates received by ordering service
if block_size or block_time_out reached then
- Send: the new block from the ordering service to the
blockchain peers for validation and consensus
if Consensus succeed then
- Add: the new block to the distributed ledger
- Trigger: LUP smart contract to aggregate the global model
using:
## 푊
## 푟
## 푔
, 푇 푆 = LUP ( block_of_transactions, 푇 푆, 푊
## 푟−1
## 푔
## )
- Validate: the aggregated global model 푊
## 푟
## 푔
using PBFT
consensus
- Save: the validated global model 푊
## 푟
## 푔
in the distributed
## IPFS
- Notify: clients to download the new version of the global
model 푊
## 푟
## 푔
end
end
end
—————————— Client: DT ————————
- Collect: local data from the associated devices
- Download: the updated global model parameters 푊
## 푟
## 푔
from the
distributed IPFS
- Assign: local model parameters 푊
## 푚
with 푊
## 푟
## 푔
for  each client / DT 푚 in 1, ..., 푀 in parallel do
while 푒≤퐸 do
- For each minibatch 휉 of size 퐿 in local dataset 푑
## 푚
end
## 16.푔
## 푚
## ←∇푓
## 푚
## (푊
## 푟
## 푔
## , 휉)
## 17.푊
## 푚
## =푊
## 푚
## −휂푔
## 푚
end
## 18. Send: 푊
## 푚
to the associated blockchain peer for endorsement
- Send: endorsed 푊
## 푚
to the ordering service for including it in the
new block
agreed upon, they store the global model in IPFS, which is ready for
download by the DT entities to commence a new training round.
Local Updates Purify (LUP):  LUP (Fig.  2 and Algorithm 2) primar-
ily focuses on analyzing the magnitude and statistical characteristics
of local updates from FL participants to discern and exclude malicious
updates from model aggregation. It employs two filtering mechanisms:
the first relies on MAD of the norm of local updates. To complement
this, the second filter utilizes statistical features extracted from these
Algorithm 2 LUP - Aggregation Scheme
Input: block_of_transactions: 푊
## 푟
, latest Trust Score for the clients: 푇 푆,
and latest global model: 푊
## 푔
Output: Updated global model aggregated by list of benign models:
## 푊
## 푔
and updated Trust Score for the clients: 푇 푆
Function LUP(block_of_transactions, 푇 푆, 푊
## 푔
## ):
## 1. Set 푊
## 푟
← block_of_transactions
## 2. Initialize: 퐼
## 푏푒
## ←[  ]
- Compute the 퐿
## 2
norm for all local updates in 푊
## 푟
## 4.퐼
## 푏푒
← Apply MAD filter as in equations (2) and (3)
## 5.푊
## 푟,푏푒
## ←푊
## 푟
## [퐼
## 푏푒
## ]
- Extract statistical features for each model in 푊
## 푟,푏푒
## :
## 7.푓 푒푎푡푢푟푒푠←
## {
extract_stats
## (
## 푊
## 푟,푏푒
## [푚]
## )}
## 푀
## 푚=1
– Each feature vec-
tor includes: positive count, negative count, zero count, kurtosis,
skewness, 퐿
## 2
norm, absolute deviation
- Apply clustering:
9.푐푙푢푠푡푒푟푠←AgglomerativeClustering(푓 푒푎푡푢푟푒푠)
## 10.퐼
## 푏푒
← Select the honest cluster based on Trust Score, absolute
deviation from 푊
## 푔
, and cosine similarity
- Update the Trust Score (TS) for the honest cluster using DoD in
equations (4) and (5): 푇 푆←푇 푆+퐷표퐷 푇 푆[퐼
## 푏푒
## ]←푇 푆[퐼
## 푏푒
## ] + 1
- Apply gradient clipping on 푊
## 푟
## [퐼
## 푏푒
] using equations (6) and (7)
## 13. Set 푊
## 푟,푏푒
## ←푊
## 푟
## [퐼
## 푏푒
## ]
## 14. Aggregate: 푊
## 푔
## =
## ∑
len(푊
## 푟,푏푒
## )
## 푖=1
## 푊
## 푟,푏푒
## [푖]
len(푊
## 푟,푏푒
## )
return 푊
## 푔
## , 푇 푆
## End Function
updates. These features are then subjected to AHC for further refine-
ment, with the input for the second filter being the output of the initial
MAD-based filter to enhance purification.
Additionally, LUP introduces the Degree of Deviation (DoD) concept
to assign a trust score (TS) to each participant, particularly those
clustered as honest. DoD is computed as the absolute deviation between
each local model update and the latest global model, with an additional
factor of one included to bolster trust in participants classified as
honest. Moreover, the selection of the honest cluster is guided by
the genuine criterion Eq. I, which evaluates trustworthiness based on
multiple statistical indicators, rather than relying on majority-based
assumptions commonly adopted in existing approaches. Upon comple-
tion of LUP, the filtered and purified local models undergo clipping
using the median as the clipping limit before being aggregated using
FedAvg to generate the global model. This two-stage filtration ensures
the identification of honest participants, contributing to the integrity
and reliability of the global model aggregation process.
4.1. DT-BFL workflow
The DT-BFL workflow (as depicted in Algorithm 1) starts by initial-
izing trust scores for all clients to zero (Line 1), and setting the initial
global model parameters 푊
## 0
## 푔
(Line 2). The initial model 푊
## 0
## 푔
is then sent
to all DT clients for local training (Line 3). The workflow proceeds in
communication rounds where, for each round, the local model updates
are received from the clients (Line 4). These updates are organized and
## Ad Hoc Networks 178 (2025) 103934
## 6

W. Issa et al.
Fig. 2. LUP Workflow.
stacked by the ordering service (Line 5). If the block size or a timeout
is reached, the block is sent to blockchain peers for validation (Line 6).
Once consensus is reached, the new block is added to the blockchain
(Lines 7–8). The LUP smart contract is then triggered to aggregate the
global model using the local updates and the clients’ trust scores (Line
## 8).
The aggregated global model 푊
## 푟
## 푔
is validated using the PBFT con-
sensus protocol (Line 9). After validation, the model is saved in the
distributed IPFS (Line 10). Clients are notified to download the updated
global model 푊
## 푟
## 푔
(Line 11). As this occurs, clients collect local data
(Line 12), download the updated global model (Line 13), and update
their local model parameters accordingly (Line 14). Clients then train
their models on minibatches of their local datasets, adjusting the model
based on the computed gradients 푔
## 푚
## =  ∇푓
## 푚
## (
## ̃
## 푊
## 푟
## 푔
, 휉) (Line 16) and
updating their models using gradient descent 푊
## 푚
## =푊
## 푚
## −휂푔
## 푚
(Line 17).
After training, the updated model is sent to the blockchain peers for
endorsement (Line 18) and added to the ordering service for inclusion
in the next block (Line 19).
The LUP process (Algorithm 2) begins by taking the block of trans-
actions 푊
## 푟
, the latest trust scores 푇 푆, and the global model 푊
## 푔
as inputs
(Line 1). An empty list 퐼
## 푏푒
is initialized to store the indices of benign
models (Line 2).
The function computes the 퐿
## 2
norm for all local updates in 푊
## 푟
to
measure their magnitude (Line 3). The MAD filter is applied initially
to filter malicious updates. The MAD is computed as:
## 푀퐴퐷=med
## (
## [
## ‖
## ‖
## 푊
## 푟,푚
## ‖
## ‖
## 2
## ]
## 푀
## 푚=1
## −med
## (
## [
## ‖
## ‖
## 푊
## 푟,푚
## ‖
## ‖
## 2
## ]
## 푀
## 푚=1
## ))
## (2)
The MAD filter then excludes updates whose 퐿
## 2
norms are not
within the acceptable range, which is given by:
med
## (
## [
## ‖
## ‖
## 푊
## 푟,푚
## ‖
## ‖
## 2
## ]
## 푀
## 푚=1
## )
## −푀퐴퐷≤
## ‖
## ‖
## 푊
## 푟,푚
## ‖
## ‖
## 2
## ≤med
## (
## [
## ‖
## ‖
## 푊
## 푟,푚
## ‖
## ‖
## 2
## ]
## 푀
## 푚=1
## )
## +푀퐴퐷
## (3)
Next, the initial benign updates are extracted (Line 5). For each
of these updates, statistical features such as positive/negative counts,
kurtosis, skewness, 퐿
## 2
norm, and absolute deviation from the global
model 푊
## 푔
are extracted (Lines 6–7). These features are then used for
clustering using agglomerative clustering (Line 9). The cluster that
best aligns with the global model is selected based on trust score,
deviation from the global model, and cosine similarity (Line 10) and it
is considered as benign/honest cluster based on the genuine criterion.
The genuine criterion Box  I is a decision rule that determines which
cluster is genuine based on the comparison of parameters similarity,
kurtosis, and deviation metrics between two clusters. The equation
compares the parameters similarity between two clusters, grad_sim_1
and grad_sim_2, where higher values indicate more alignment with the
global learning direction. It also considers the kurtosis values, kurt_1
and kurt_2, of each cluster’s model updates, where higher kurtosis
suggests more concentration of updates around a few points, signaling
stability in learning. Lastly, the deviation values dev_1 and dev_2 mea-
sure how far each cluster’s model updates are from the global model,
with smaller values indicating better alignment. In this criterion, TS
acts as a precondition, ensuring that Cluster 2 is only considered
genuine if its TS is greater than or equal to that of Cluster 1, thereby
prioritizing clusters that are more historically reliable.
According to the genuine criterion Box  I, if Cluster 2 has a higher
parameters similarity and either greater kurtosis or lower deviation
than Cluster 1, it is considered genuine. Alternatively, if Cluster 2 has
a higher parameters similarity and a lower deviation than Cluster 1, it
is also regarded as genuine. In all other cases, Cluster 1 is considered
genuine. This decision rule ensures that the genuine cluster is selected
based on its relative performance in terms of update alignment and sta-
tistical characteristics, making it robust and reducing conflicts during
model aggregation, however, proposing a perfect genuine criterion still
needs more research efforts.
The trust scores of the clients in the selected cluster are updated
using the Degree of Deviation (DoD), which is computed as:
## 퐷푒푔푟푒푒 표푓 퐷푒푣푖푎푡푖표푛(퐷표퐷) = 1 −
## 1
## 1 +퐴퐷
## (4)
where 퐴퐷 represents the Absolute Deviations (AD), given by:
## 퐴푏푠표푙푢푡푒 퐷푒푣푖푎푡푖표푛푠(퐴퐷) =
## [
## |
## |
## |
## 푊
## 푟,푚
## −푊
## 푔
## |
## |
## |
## ]
## 푀
## 푚=1
## (5)
The trust scores are then updated accordingly (Line 11). Afterwards,
gradient clipping is applied to ensure that the gradients are within the
specified bounds. The clipping threshold 퐶
## 푏
is computed as:
## 퐶
## 푏
←Median
## (
## ‖
## ‖
## 푊
## 푟
## [퐼
## 푏푒
## ]
## ‖
## ‖
## 2
## )
## (6)
The gradients are clipped by scaling the updates to ensure that their
## 퐿
## 2
norm does not exceed 퐶
## 푏
, as follows:
## 푊
## 푟
## [퐼
## 푏푒
## ]←푊
## 푟
## [퐼
## 푏푒
] ∕ max
## (
## 1,
## ‖
## ‖
## 푊
## 푟
## [퐼
## 푏푒
## ]
## ‖
## ‖
## 2
## 퐶
## 푏
## )
## (7)
Finally, the benign updates are aggregated by computing the aver-
age of the selected clients (Line 14):
## 푊
## 푔
## =
## ∑
len(푊
## 푟,푏푒
## )
## 푖=1
## 푊
## 푟,푏푒
## [푖]
len(푊
## 푟,푏푒
## )
## (8)
The updated global model 푊
## 푔
and the updated trust scores 푇 푆
are returned (Line 14). Thus, LUP ensures that the global model is
updated using the most trustworthy local updates while maintaining
the integrity of the entire federated learning process.
- Experimental setup
Deep Learning Models and Datasets: The framework’s perfor-
mance is assessed using the MNIST and CIFAR-10 datasets, employing
Convolutional Neural Network (CNN) architecture(CNN model is com-
posed of three convolutional layers, each followed by max-pooling,
and three fully connected layers utilizing Rectified Linear Unit (ReLU)
activations) and ResNet models respectively. The ToN-IoT [36] is
also employed with the MLP model. Moreover, complex models like
## Ad Hoc Networks 178 (2025) 103934
## 7

W. Issa et al.
## Table 2
Details of various datasets for experimental evaluation.
DatasetTrainTestInput SizeClassesModelTarget
MNIST50,00010,00028 × 2810CNNImage Classification
Cifar-1050,00010,00032 × 32 × 310LeNet, DenseNet121, and ResNet-9Image Classification
ToN-IoT368,74092,20944 × 110MLPIntrusion Detection
## Table 3
Settings for key hyper-parameters.
Hyper-parameterDescriptionValue
MTotal Number of FL participants50
FPercentage of compromised devices50%
휂Learning Rate0.001–0.01
퐵The local batch size128,256
푅The number of global rounds100
푆The Skew degree of Non-IID50%
DenseNet121 and ResNet-9 are employed to evaluate the LUP’s effec-
tiveness against poisoning attacks. Table  2 summarizes these datasets
along with the models used.
FL Hyperparameters:  We establish a federated learning setup
with 50 participants (푀= 50). The global model undergoes training
for 100 communication rounds (푅= 100) using the Adam optimizer
with a learning rate set to (휂= 0.001) and a batch size of 256 (퐿=
256). Furthermore, data distribution is non-IID, where a portion ’푆’ is
randomly divided in an IID manner. In contrast, the remaining portion
(1−푆) is divided into different shards based on labels, with each client
assigned different shards. The hyperparameters used in training, along
with their values, are summarized in Table  3.
Threat Model:  In this research, the threat model encompasses
attackers aiming to compromise the integrity of model training by
flipping labels or maliciously manipulating trained parameters. In this
context, attackers may gain access to certain digital twins and manipu-
late local parameters before transmitting them to blockchain peers for
subsequent validation and filtration. Additionally, attackers may lack
sufficient knowledge about the aggregation rule implemented in the
decentralized smart contract.
Blockchain Network: Implementing the blockchain network within
DT-BFL utilizes Hyperledger Fabric,
## 1
a decentralized, modular frame-
work tailored for permissioned blockchain networks. In Hyperledger
Fabric, clients, acting as FL participants or DT entities, propose trans-
actions and submit them to the ordering service. Meanwhile, peers,
represented by edge servers, maintain the distributed ledger and ex-
ecute smart contract logic. A membership service provider assigns
each entity within the Fabric network identity and uses a public Key
Infrastructure (PKI) to authenticate the actions of all network partic-
ipants. Additionally, all identities in the Fabric network are backed
by a valid root of trust established through a certificate authority
(CA), ensuring that the certificates originate from an organization (edge
server/peer) that is a network member. In our implementation, we
simulate 50 federated learning DT participants using Python, with
their interactions with the Fabric network via RESTful APIs, developed
in the Python-Flask platform. Specifically, Fabric networks typically
consist of three peer organizations (edge servers or validators) and
an ordering service. Furthermore, we installed IPFS on Ubuntu by
utilizing the official version available on the IPFS website
## 2
. To evaluate
the performance of the blockchain network, we leverage Hyperledger
## Caliper
## 3
, a blockchain benchmarking tool that assesses the efficiency
of the blockchain network using various metrics including transaction
rate per second (TPS), throughput, and latency.
## 1
https://hyperledger-fabric.readthedocs.io/en/release-2.5/
## 2
https://docs.ipfs.tech/
## 3
https://www.hyperledger.org/projects/caliper
Fig. 3. Average throughput vs. latency using different numbers of clients.
Fig. 4. Impact of Transaction Arrival Rate (TAR) on average throughput.
We have implemented the smart contracts using the Node.js SDK,
except for the smart contract of LUP, implemented using Python. This
decision was made due to the complex logic involved in LUP, which is
more easily implemented in Python than in Node.js. To send notifica-
tions to FL participants (i.e., clients of the Fabric network), we utilized
event management in Hyperledger Fabric. This approach allows us to
push notifications to all clients once the global model is calculated and
stored in IPFS.
- Experimental results and discussion
Transaction Latency and Throughput Analysis: Figs.  3and
4 depict the evolving trends of latency, measured in seconds and
throughput, denoted in Transactions Per Second (TPS), across varying
transaction arrival rates and different levels of client participation.
Throughput measures how many transactions are processed within a
given timeframe typically expressed as transactions per second. Here,
as the number of nodes increases from 50 to 150, the throughput
decreases slightly, and when the number of nodes increases from
200 to 250, the throughput decreases significantly. Specifically, the
throughput decreases from 648 transactions per second at 50 nodes to
107.3 transactions per unit of time at 250 nodes. Moreover, latency
denotes the duration required for a transaction to undergo processing
and subsequent commitment to the ledger. Conversely, latency tends to
increase throughput as the number of nodes increases. At 50 nodes, the
## Ad Hoc Networks 178 (2025) 103934
## 8

W. Issa et al.
## Table 4
Evaluating defense approaches against diverse model poisoning attacks: Malicious participants percentage: 50%, Non-IID level: 50% (i.e. 50% of the data in an
IID manner, while the remainder is allocated using a sort-and-partition method) on diverse models and datasets.
DatasetDefenseYearNo AttackPoisoning Attacks [37,38]
(Model)RandomNoiseLabel-FlipByzMeanSign-FlipLIEMin-MaxMin-SumMPAF
## Mean [39]201797.44%18.18%20.67%36.86%9.8%9.8%95.75%94.35%96.45%9.8%
Multi-Krum [32]201784.78%97.87%98.08%14.46%97.73%11.35%69.03%78.06%10.32%97.64%
TrMean [40]201811.35%11.35%11.35%11.35%11.35%11.35%9.8%11.35%11.35%9.8%
## Median [40]201897.41%97.95%98.11%43.24%97.82%11.35%46.09%67.94%70.05%97.81%
MNISTDnC [13]202197.27%88.41%94.97%37.91%97.87%11.35%95.43%94.29%86.94%9.8%
GeoMed [41]202297.11%98.16%97.89%74.64%97.81%96.33%60.84%49.71%9.8%97.25%
SignGuard [42]202298.0%11.35%11.35%31.21%11.35%11.35%77.77%33.25%33.30%11.35%
ClipCluster [43]202496.44%16.61%17.68%61.66%97.53%96.51%97.53%97.60%93.12%97.71%
## LUP202597.90%98.38%97.97%98.25%98.07%98.03%97.97%97.90%97.67%97.97%
## Mean [39]201799.72%65.07%99.67%41.68%65.07%65.07%99.70%99.21%99.32%65.07%
Multi-Krum [32]201799.98%99.98%99.98%56.99%99.48%65.07%99.98%99.98%99.98%99.98%
TrMean [40]201865.07%65.07%65.07%85.09%65.07%65.07%65.07%65.07%65.07%65.07%
## Median [40]201899.98%99.97%99.88%36.54%99.49%4.33%98.94%98.65%98.83%99.98%
ToN-IoTDnC [13]202199.98%99.42%99.98%63.72%99.98%4.33%99.98%99.98%99.98%65.05%
GeoMed [41]202299.98%99.98%99.98%94.30%99.98%68.66%99.98%99.98%99.98%99.98%
SignGuard [42]202299.98%98.68%65.07%92.31%65.07%65.07%99.98%99.98%99.98%65.07%
ClipCluster [43]202499.98%65.07%65.07%99.39%99.89%98.96%99.98%99.98%99.98%62.29%
## LUP202599.99%99.98%99.98%99.58%99.98%99.97%99.97%99.98%99.98%99.98%
Fig. 5. Attack impact on various defense approaches against poisoning attacks.
latency is 0.37 s, which increases to 3.03 s at 250 nodes. The increase
in latency indicates that transactions take longer to be processed as the
system scales up, which could be due to increased network congestion
or resource contention (Fig.  3).
In Fig.  4, the throughput remains relatively stable, around 450 to
460 transactions per second (TPS), as the arrival rate increases from
50 to 150. This indicates that the system can handle the incoming
transactions efficiently within this range. However, the throughput
declines gradually as the transaction arrival rate increases beyond
- This decline becomes more pronounced as the transaction arrival
rate reaches 250, dropping to 389.1. The latency remains consistently
low at 0.01 to 0.02 s across most transaction arrival rates, indicating
quick transaction processing and ledger commitment. However, as the
transaction arrival rate surpasses 200, there is a noticeable increase in
latency. At a transaction arrival rate of 250, the latency reaches 0.1 s,
indicating a delay in processing. This increase in latency suggests that
the system may be experiencing congestion or resource contention at
higher transaction arrival rates, leading to slower transaction process-
ing times. This occurs because the transaction queue becomes blocked,
leading to increased waiting times per transaction and a consequent
gradual decrease in average throughput. As the number of transactions
waiting in the queue increases, each transaction spends more time
waiting to be processed. This increased waiting time contributes to
higher latency and reduced throughput as transactions take longer.
Robustness and Performance Evaluation:  We conducted experi-
ments on the ToN-IoT and MNIST datasets using Multilayer Perceptrons
(MLP) and Convolutional Neural Networks (CNN) to evaluate the ef-
fectiveness of LUP against various poisoning attacks. The MLP model
consists of five linear layers, four batch normalization layers, four ReLU
layers, three dropout layers, and one softmax layer. Conversely, the
CNN architecture comprises three convolutional layers, each accompa-
nied by max-pooling, and three fully connected layers utilizing Recti-
fied Linear Unit (ReLU) activations. The conducted poisoning attacks
encompass Random, Noise, ByzMean, Min-Sum, Min-Max, Label-Flip,
Sign-Flip, LIE [37], and MPAF [38], aiming to scrutinize the resilience
of the LUP method across different adversarial scenarios. For both
datasets, we utilize 50 federated learning (FL) participants, a learning
rate of 1푒
## 3
, 100 communication rounds, 1 local training epoch, and the
Adam optimizer. Additionally, we employ a batch size of 256 for the
ToN-IoT dataset and 128 for MNIST. The LUP algorithm is implemented
using PyTorch and Python. To ensure fairness and consistency in the
comparative analysis, all approaches were evaluated under identical
experimental conditions on the same hardware platform.
## Ad Hoc Networks 178 (2025) 103934
## 9

W. Issa et al.
## Table 5
Comparison of Error Rates among different aggregation schemes under diverse poisoning attacks. (Red cells with ↑ indicate high
error rates ⩾ 50%, Green cells with ↓ indicate low error rates < 50%). The LUP row is fully shaded to highlight its consistently low error
rates.
SchemeRandomNoiseLabel-FlipByzMeanSign-FlipLIEMin-MaxMin-SumMPAF
## Mean↑81.34↑78.79↑62.17↑89.94↑89.94↓1.73↓3.17↓1.02↑89.94
TrMean↑88.35↑88.35↑88.35↑88.35↑88.35↑89.94↑88.35↑88.35↑89.94
## Median↓0.52↓0.69↑55.62↓0.39↑88.35↑52.70↓30.28↓28.11↓0.38
GeoMed↓0.74↓0.46↓23.40↓0.38↓1.14↑37.56↑48.98↑89.94↓0.19
Multi-Krum↓0.44↓0.66↑85.16↓0.30↑88.35↑29.16↓19.89↑89.41↓0.21
ClipCluster↑82.95↑81.86↓36.72↓0.09↓0.95↓0.90↓0.16↓4.43↓0.28
SignGuard↑88.35↑88.35↑67.97↑88.35↑88.35↓20.19↑65.88↑65.83↑88.35
DnC↓9.27↓2.53↑61.09↓0.44↑88.35↓2.06↓3.23↓10.78↑89.94
## LUP↓0.96↓0.54↓0.83↓0.65↓0.61↓0.54↓0.47↓0.24↓0.54
Fig. 6. Evaluating training stability: a comparison of LUP with State-of-the-art schemes on MNIST dataset.
As shown in Table  4, our analysis using the ToN-IoT dataset high-
lights LUP’s strong ability to reduce the impact of various poisoning
attacks while maintaining model accuracy. Unlike other defense meth-
ods, LUP consistently performs well across different attack scenarios.
For example, while methods like SignGuard fail to handle certain
attacks such as Noise, MPAF, Sign-Flip, and ByzMean, LUP successfully
defends against all of them. Similarly, on the MNIST dataset, LUP
shows reliable protection against all tested poisoning attacks. In con-
trast, other approaches may be effective against some attacks but not
others. These results show LUP’s versatility and strength in protecting
federated learning models from a wide range of adversarial threats.
Attack Impact:  The attack impact metric quantifies the decrease
in the accuracy of the global model resulting from the attack. It
is computed as the disparity between the highest accuracy attained
by the global model across all FL training rounds when no attack
is present and the maximum achievable accuracy under the specific
attack. A smaller disparity in test accuracy between the global model
under attack and this without any attack indicates a more resilient
and reliable aggregation algorithm. Fig.  5 illustrates the attack impact
rates of different poisoning attacks on the MNIST dataset. We noted
that traditional mean aggregation algorithms like FedAvg and TrMean
are highly susceptible to poisoning attacks. Although other aggregation
algorithms can alleviate the effects of poisoning attacks, they are still
affected to varying degrees. Remarkably, LUP exhibits robustness and
remains unaffected by any tested poisoning attacks. This observation is
also consistent across the ToN-IoT dataset.
Error Rate (ER): The error rate represents the percentage of dis-
crepancy between the accuracy of the model under attack and the
accuracy of the model without any attacks. Thus, the error rate indi-
cates how much the model’s performance deviates from its expected or
normal behavior, with higher error rates indicating greater degradation
in performance due to the attack. Therefore, the ER can be defined by
the following equation:
Error rate (%)=
## (
## 1 −
True model accuracy
Model under attack accuracy
## )
## × 100(9)
From Table  5, we can observe significant variations in error rates
across different schemes. The Mean aggregation scheme showed vul-
nerability to poisoning, with error rates ranging from 1.02% to 89.94%
## Ad Hoc Networks 178 (2025) 103934
## 10

W. Issa et al.
## Table 6
Evaluating LUP against diverse Model poisoning attacks: malicious participants percentage: 50%, Non-IID level: Random Sampling on DenseNet
and ResNet-9 for Cifar-10.
ModelNo AttackPoisoning Attacks
RandomNoiseLabel-FlipByzMeanSign-FlipLIEMin-MaxMin-SumMPAF
DenseNet12179.15%79.18%79.24%79.11%79.38%79.01%77.87%79.90%81.03%79.22%
ResNet-976.09%73.04%72.90%76.10%73.93%69.85%70.17%74.19%72.29%68.47%
Fig. 7. Comparing execution time: LUP vs. state-of-the-art schemes.
across various attacks. Conversely, the TrMean scheme demonstrated
consistent error rates of 88.35% across different attacks, indicating
its susceptibility to poisoning attempts. Other schemes, such as Multi-
Krum, exhibited mixed performance, performing well under most at-
tacks but showing higher error rates under specific scenarios, like
Label-Flip attacks. ClipCluster displayed a unique pattern with excep-
tionally low error rates under Random and Noise attacks but signifi-
cantly higher rates under Label-Flip and Min-Sum attacks. SignGuard
demonstrated relatively high error rates under certain attacks, like
Label-Flip (67.97%), but lower rates under others, such as Random and
Noise. In contrast, LUP emerged as a robust aggregation scheme with
consistently low error rates across all attacks, ranging from 0.24% to
## 0.96%.
Training Stability: Fig.  6 illustrates the performance of LUP and
its related schemes, demonstrating its robustness in achieving stable
training and performance on the test dataset across communication
rounds, even in the presence of poisoning attacks affecting 50% of
the FL participants. In the case of the ByzMean attack, both LUP
and DnC demonstrate comparable and stable performance, with Clip-
Cluster also achieving reasonable performance. However, SignGuard
and Multi-Krum are adversely affected by this attack. Regarding Min-
Max, Min-Sum, and LIE attacks, ClipCluster and LUP exhibit compa-
rable performance, showcasing their resilience against these attacks,
while DnC, SignGuard, and Multi-Krum are impacted. Additionally,
LUP demonstrates superior robustness and performance against Sign-
Flip and Label-Flip attacks, whereas the other schemes are vulnerable
to both attacks, failing to achieve stable performance during training.
In summary, our findings indicate that LUP effectively mitigates the
harm of poisoning attacks on global model aggregation compared to
other schemes, which may succeed or fail inconsistently in this regard.
Execution Time:  The LUP aggregation scheme involves two fil-
tration stages, as discussed in the previous section. Consequently, it
naturally requires more execution time than its simpler counterparts
across the communication rounds. In Fig.  7, we present the execution
## Table 7
Computational complexity of DT-BFL and LUP.
ComponentComplexity
DT-BFL (total)
## (
## 푅⋅
## (
## 푀⋅퐸⋅
## 퐷
## 푚
## 퐿
## ⋅퐶+푁
## 2
## +LUP
## ))

LUP Aggregation
## (
## 푀
## 2
log푀+푀⋅푑
## )

times of LUP and its related schemes. While LUP does indeed incur
a higher execution time than its counterparts, it remains within a
reasonable range, not surpassing 0.26 s.
Evaluating LUP on More Complex Models:  We conducted ex-
periments with two popular models, DenseNet121 and ResNet-9, to
test how well LUP works with complex models. The results, shown
in Table  6, demonstrate that LUP effectively reduces the impact of
poisoning attacks on the Cifar-10 dataset. It also helps lessen the effects
of Label-Flip attacks when using complex models like DenseNet121 and
ResNet-9. However, while LUP reduces the impact of Sign-Flip attacks,
there is still a small effect on the overall accuracy of the global model.
Computational Complexity of DT-BFL: The computational com-
plexity of DT-BF (Table  7) arises from both the client-side local training
and the blockchain-based network. Each of the 푀 clients performs local
training over 퐸 epochs with mini-batches, resulting in a complexity
of 
## (
## 푀⋅퐸⋅
## 퐷
## 푚
## 퐿
## ⋅퐶
## )
, where 퐷
## 푚
is the size of the local dataset, 퐿
is the batch size, and 퐶 is the cost of a single forward–backward
pass. In addition, during each of the 푅 global rounds, clients submit
updates that are validated and aggregated via a blockchain network.
This includes running consensus protocols like PBFT (with complexity
## (푁
## 2
)) and executing smart contracts, which adds further overhead.
Therefore, the total cost per round includes local training, blockchain
consensus, and global model aggregation.
The LUP aggregation scheme, used within DT-BFL, introduces its
own computational overhead. It begins by filtering outliers using MAD,
which involves computing 퐿
## 2
norms and medians with complexity
(푀log푀+푀⋅푑), where 푑 is the model dimensionality. It then extracts
statistical features and clusters the updates using agglomerative clus-
tering, which has a complexity of (푀
## 2
log푀). Trust scores are then
updated, and the filtered updates are aggregated. The clustering step is
the most computationally expensive, making the total LUP complexity
approximately (푀
## 2
log푀+푀⋅푑)—efficient for moderate client sizes,
but potentially demanding for large-scale federated learning systems.
## 7. Conclusion
This study has introduced a novel Digital Twin-driven Blockchain-
enabled Federated Learning (DT-BFL) framework designed to safeguard
IoT networks. The framework aims to create a digital twin represen-
tation of IoT devices, enabling real-time, secure, and decentralized
federated learning. This is achieved through permissioned blockchain
technology and its decentralized smart contracts. Furthermore, DT-
BFL incorporates LUP as a robust aggregation mechanism. Thus, LUP
alleviates the effects of poisoning attacks and facilitates the aggre-
gation of a reliable global model. Our experimental results demon-
strate that LUP consistently outperforms state-of-the-art aggregation
schemes across multiple datasets and model architectures, including
## Ad Hoc Networks 178 (2025) 103934
## 11

W. Issa et al.
CNNs, MLPs, ResNets, and DenseNets. Even under adversarial settings
where up to 50% of participants are compromised, LUP maintains
model integrity through a two-stage filtering process (MAD and AHC)
supported by a genuine criterion and trust scoring mechanism. These
evaluations underscore DT-BFL’s practical utility for secure edge intel-
ligence. Future work will enhance the genuine criterion with adaptive
scoring and replace costly clustering with a lightweight scheme while
optimizing runtime for scalable, real-time deployment in dynamic IoT
environments.
CRediT authorship contribution statement
Wael Issa: Writing – original draft, Visualization, Valida-
tion, Methodology, Investigation, Conceptualization. Nour Moustafa:
Writing – review & editing, Validation, Supervision, Investigation.
Benjamin Turnbull: Writing – review & editing, Validation, Super-
vision, Methodology. Kim-Kwang Raymond Choo: Writing – review
& editing, Conceptualization.
Declaration of competing interest
The authors declare they have no known competing financial inter-
ests or personal relationships that could have appeared to influence the
work reported in this paper.
Data availability
Data is public and available.
## References
[1]Dinh C. Nguyen, Ming Ding, Pubudu N. Pathirana, Aruna Seneviratne, Jun
Li, Dusit Niyato, Octavia Dobre, H. Vincent Poor, 6G internet of things: A
comprehensive survey, IEEE Internet Things J. 9 (1) (2022) 359–383.
[2]Sawsan AbdulRahman, Safa Otoum, Ouns Bouachir, Azzam Mourad, Management
of digital twin-driven IoT using federated learning, IEEE J. Sel. Areas Commun.
## 41 (11) (2023) 3636–3649.
[3]Yunlong Lu, Xiaohong Huang, Ke Zhang, Sabita Maharjan, Yan Zhang, Low-
latency federated learning and blockchain for edge association in digital twin
empowered 6G networks, IEEE Trans. Ind. Inform. 17 (7) (2021) 5098–5107.
[4]Gartner, Gartner survey reveals digital twins are entering mainstream use, 2020.
[5]Elif Ak, Kübra Duran, Octavia A. Dobre, Trung Q. Duong, Berk Canberk, T6CONF:
Digital twin networking framework for IPv6-enabled net-zero smart cities, IEEE
## Commun. Mag. 61 (3) (2023) 36–42.
[6]Long Zhang, Han Wang, Hongmei Xue, Hongliang Zhang, Qilie Liu, Dusit Niyato,
Zhu Han, Digital twin-assisted edge computation offloading in industrial internet
of things with NOMA, IEEE Trans. Veh. Technol. 72 (9) (2023) 11935–11950.
[7]Sergio Infante, Julia Robles, Cristian Martín, Bartolomé Rubio, Manuel Díaz,
Distributed digital twins on the open-source OpenTwins framework, Adv. Eng.
## Inform. 64 (2025) 102970.
[8]Su Wang, Seyyedali Hosseinalipour, Vaneet Aggarwal, Christopher G. Brinton,
David J. Love, Weifeng Su, Mung Chiang, Toward cooperative federated learning
over heterogeneous edge/fog networks, IEEE Commun. Mag. 61 (12) (2023)
## 54–60.
[9]Xinyang Cao, Lifeng Lai, Distributed gradient descent algorithm robust to an
arbitrary number of Byzantine attackers, IEEE Trans. Signal Process. 67 (22)
## (2019) 5850–5864.
[10]Cong Xie, Sanmi Koyejo, Indranil Gupta, Zeno: Distributed stochastic gradient
descent with suspicion-based fault-tolerance, in: Kamalika Chaudhuri, Ruslan
Salakhutdinov (Eds.), Proceedings of the 36th International Conference on
Machine Learning, in: Proceedings of Machine Learning Research, vol. 97, PMLR,
2019, pp. 6893–6901.
[11]Shenghui Li, Edith Ngai, Thiemo Voigt, Byzantine-robust aggregation in federated
learning empowered industrial IoT, IEEE Trans. Ind. Inform. 19 (2) (2023)
## 1165–1175.
[12]Felix Sattler, Klaus-Robert Müller, Thomas Wiegand, Wojciech Samek, On the
Byzantine robustness of clustered federated learning, in: ICASSP 2020 - 2020
IEEE International Conference on Acoustics, Speech and Signal Processing,
ICASSP, 2020, pp. 8861–8865.
[13]Virat Shejwalkar, Amir Houmansadr, Manipulating the Byzantine: Optimizing
model poisoning attacks and defenses for federated learning, in: NDSS, 2021.
[14]Gilad Baruch, Moran Baruch, Yoav Goldberg, A little is enough: Circumventing
defenses for distributed learning, in: H. Wallach, H. Larochelle, A. Beygelzimer, F.
dÁlché Buc, E. Fox, R. Garnett (Eds.), Advances in Neural Information Processing
Systems, vol. 32, Curran Associates, Inc, 2019.
[15]Lopamudra Praharaj, Maanak Gupta, Deepti Gupta, Hierarchical federated trans-
fer learning and digital twin enhanced secure cooperative smart farming, in: 2023
IEEE International Conference on Big Data, BigData, 2023, pp. 3304–3313.
[16]Xiaoge Huang, Yuhang Wu, Chengchao Liang, Qianbin Chen, Jie Zhang, Distance-
aware hierarchical federated learning in blockchain-enabled edge computing
network, IEEE Internet Things J. 10 (21) (2023) 19163–19176.
[17]Collin Meese, Hang Chen, Wanxin Li, Danielle Lee, Hao Guo, Chien-Chung Shen,
Mark Nejad, Adaptive traffic prediction at the ITS edge with online models
and blockchain-based federated learning, IEEE Trans. Intell. Transp. Syst. (2024)
## 1–16, Early Access.
[18]Yunlong Lu, Xiaohong Huang, Ke Zhang, Sabita Maharjan, Yan Zhang, Blockchain
empowered asynchronous federated learning for secure data sharing in internet
of vehicles, IEEE Trans. Veh. Technol. 69 (4) (2020) 4298–4311.
[19]Youyang Qu, Shui Yu, Longxiang Gao, Keshav Sood, Yong Xiang, Blockchained
dual-asynchronous federated learning services for digital twin empowered
edge-cloud continuum, IEEE Trans. Serv. Comput. (2024) 1–14, Early Access.
[20]Yunlong Lu, Xiaohong Huang, Ke Zhang, Sabita Maharjan, Yan Zhang,
Communication-efficient federated learning and permissioned blockchain for
digital twin edge networks, 8, (4) 2021, pp. 2276–2288.
[21]Shuiguang Deng, Hailiang Zhao, Weijia Fang, Jianwei Yin, Schahram Dustdar,
Albert Y. Zomaya, Edge intelligence: The confluence of edge computing and
artificial intelligence, IEEE Internet Things J. 7 (8) (2020) 7457–7469.
[22]Ahmed Imteaj, Urmish Thakker, Shiqiang Wang, Jian Li, M. Hadi Amini, A survey
on federated learning for resource-constrained IoT devices, IEEE Internet Things
## J. 9 (1) (2022) 1–24.
[23]Nickolaos Koroniotis, Nour Moustafa, Francesco Schiliro, Praveen Gauravaram,
Helge Janicke, The SAir-IIoT cyber testbed as a service: A novel cybertwins
architecture in IIoT-based smart airports, IEEE Trans. Intell. Transp. Syst. 24 (2)
## (2023) 2368–2381.
[24]Wael Issa, Nour Moustafa, Benjamin Turnbull, Nasrin Sohrabi, Zahir Tari,
Blockchain-based federated learning for securing internet of things: A
comprehensive survey, ACM Comput. Surv. 55 (9) (2023) 1–43.
[25]Xiaojie Wang, Hailin Zhu, Zhaolong Ning, Lei Guo, Yan Zhang, Blockchain
intelligence for internet of vehicles: Challenges and solutions, IEEE Commun.
## Surv. Tutor. 25 (4) (2023) 2325–2355.
[26]Xiumin Li, Mi Wen, Siying He, Rongxing Lu, Liangliang Wang, A privacy-
preserving federated learning scheme against poisoning attacks in smart grid,
IEEE Internet Things J. (2024) 1–12, Early Access.
[27]Xiaoyu Cao, Zaixi Zhang, Jinyuan Jia, Neil Zhenqiang Gong, Flcert: Provably
secure federated learning against poisoning attacks, IEEE Trans. Inf. Forensics
## Secur. 17 (2022) 3691–3705.
[28]Synthia Hossain Karobi, Shakil Ahmed, Saifur Rahman Sabuj, Ashfaq Khokhar,
EcoEdgeTwin: Driving 6G with AI-enhanced edge integration and sustainable
digital twins, Digit. Twins Appl. 2 (1) (2025) e70000.
[29]Rute C. Sofia, Josh Salomon, Simone Ferlin-Reiter, et al., A framework
for cognitive, decentralized container orchestration, IEEE Access 12 (2024)
## 79978–80008.
[30]Zhanpeng Yang, Yuanming Shi, Yong Zhou, Zixin Wang, Kai Yang, Trustworthy
federated learning via blockchain, IEEE Internet Things J. 10 (1) (2023) 92–109.
[31]Li Jiang, Hao Zheng, Hui Tian, Shengli Xie, Yan Zhang, Cooperative federated
learning and model update verification in blockchain-empowered digital twin
edge networks, IEEE Internet Things J. 9 (13) (2022) 11154–11167.
[32]Peva Blanchard, El Mahdi El Mhamdi, Rachid Guerraoui, Julien Stainer, Machine
learning with adversaries: Byzantine tolerant gradient descent, in: I. Guyon,
## U. Von Luxburg, S. Bengio, H. Wallach, R. Fergus, S. Vishwanathan, R. Garnett
(Eds.), Advances in Neural Information Processing Systems, vol. 30, Curran
## Associates, Inc, 2017.
[33]Wen Sun, Peng Wang, Ning Xu, Gaozu Wang, Yan Zhang, Dynamic digital twin
and distributed incentives for resource allocation in aerial-assisted internet of
vehicles, IEEE Internet Things J. 9 (8) (2022) 5839–5852.
[34]Zhihan Lv, Chen Cheng, Haibin Lv, Blockchain-based decentralized learning for
security in digital twins, IEEE Internet Things J. 10 (24) (2023) 21479–21488.
[35]Lun Tang, Mingyan Wen, Zhenzhen Shan, Li Li, Qinghai Liu, Qianbin Chen, Dig-
ital twin-enabled efficient federated learning for collision warning in intelligent
driving, IEEE Trans. Intell. Transp. Syst. 25 (3) (2024) 2573–2585.
[36]Abdullah Alsaedi, Nour Moustafa, Zahir Tari, Abdun Mahmood, Adnan Anwar,
TON_IoT telemetry dataset: A new generation dataset of IoT and IIoT for
data-driven intrusion detection systems, IEEE Access 8 (2020) 165130–165150.
[37]Jian Xu, Shao-Lun Huang, Linqi Song, Tian Lan, Byzantine-robust federated
learning through collaborative malicious gradient filtering, in: 2022 IEEE 42nd
International Conference on Distributed Computing Systems, ICDCS, IEEE, 2022,
pp. 1223–1235.
## Ad Hoc Networks 178 (2025) 103934
## 12

W. Issa et al.
[38]Xiaoyu Cao, Neil Zhenqiang Gong, Mpaf: Model poisoning attacks to federated
learning based on fake clients, in: Proceedings of the IEEE/CVF Conference on
Computer Vision and Pattern Recognition, 2022, pp. 3396–3404.
[39]Brendan McMahan, Eider Moore, Daniel Ramage, Seth Hampson, Blaise Aguera
y Arcas, Communication-efficient learning of deep networks from decentralized
data, in: Artificial Intelligence and Statistics, PMLR, 2017, pp. 1273–1282.
[40]Dong Yin, Yudong Chen, Ramchandran Kannan, Peter Bartlett, Byzantine-
robust distributed learning: Towards optimal statistical rates, in: International
Conference on Machine Learning, PMLR, 2018, pp. 5650–5659.
[41]Krishna Pillutla, Sham M. Kakade, Zaid Harchaoui, Robust aggregation for
federated learning, IEEE Trans. Signal Process. 70 (2022) 1142–1154.
[42]Jian Xu, Shao-Lun Huang, Linqi Song, Tian Lan, Byzantine-robust federated
learning through collaborative malicious gradient filtering, in: 2022 IEEE 42nd
International Conference on Distributed Computing Systems, ICDCS, 2022, pp.
## 1223–1235.
[43]Shenghui Li, Edith C.-H. Ngai, Thiemo Voigt, An experimental study of
Byzantine-robust aggregation schemes in federated learning, IEEE Trans. Big Data
## 10 (6) (2024) 975–988.
Wael Issa received his bachelor’s and master’s degrees in
computer science from the Faculty of Computers and Artifi-
cial Intelligence at Helwan University, Cairo, Egypt, in 2013
and 2019, respectively. He received a Ph.D. in Cybersecurity
from the School of Engineering and Information Technology
(SEIT), University of New South Wales (UNSW), Canberra,
ACT, Australia, in 2025, with a focus on federated learning
and blockchain for the Internet of Things. His research
interests include artificial intelligence, privacy preservation,
and cybersecurity.
Nour Moustafa received bachelor’s and master’s degrees
in computer science from the Faculty of Computer and
Information, Helwan University, Egypt, in 2009 and 2014,
respectively, and the Ph.D. degree in cybersecurity from the
University of New South Wales (UNSW) Canberra, Canberra,
ACT, Australia, in 2017. He was a Post-Doctoral Fellow at
UNSW Canberra from June 2017 to December 2018. He
is currently the Coordinator of Postgraduate Cyber Disci-
pline and the Leader of Intelligent Security at the School
of Engineering and Information Technology (SEIT), UNSW
Canberra. He has several research grants totaling over AUD
$1.2 million. His areas of interest include cybersecurity, in
particular, network security, the Internet-of Things (IoT) se-
curity, intrusion detection systems, statistics, deep learning,
and machine learning techniques.
Benjamin Turnbull is an Associate Professor at the Uni-
versity of New South Wales, Australian Defence Force,
Canberra, ACT, Australia. He is a Certified Information
Systems Security Professional (CISSP). He has been working
in digital forensics, network security, and simulation for
17 years. His previous work as a defense research scientist
saw him develop and deploy new technologies to multiple
clients globally. His research focuses on the intersection of
cybersecurity, simulation, scenario based learning, and the
security of heterogeneous devices and future networks.
Kim-Kwang Raymond Choo graduated with a Ph.D. in
information technology from Queensland University of Tech-
nology, Brisbane, QLD, Australia. He currently holds the
Cloud Technology Endowed Professorship at The University
of Texas at San Antonio, and is the founding co-Editor-in-
Chief of ACM Distributed Ledger Technologies: Research &
Practice, and the founding Chair of IEEE Technology and
Engineering Management Society’s Technical Committee on
Blockchain and Distributed Ledger Technologies.
## Ad Hoc Networks 178 (2025) 103934
## 13