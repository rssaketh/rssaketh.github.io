# Shared CV content (mirrors cv_work/main.tex). LaTeX strings.
ME = r"\me"
PHONE = (r"tel:+1(646)7372925", r"+1 (646) 737-2925")
EMAIL = (r"mailto:sakethrambhatla@gmail.com", r"sakethrambhatla@gmail.com")
WEB = (r"https://rssaketh.github.io/", r"rssaketh.github.io")
SCHOLAR = (r"https://scholar.google.com/citations?user=VRyNTogAAAAJ&hl=en", r"Google Scholar")
LINKEDIN = (r"https://www.linkedin.com/in/rssaketh/", r"linkedin.com/in/rssaketh")

JOBS = [
 ("Member of Technical Staff", "Skild AI Research", "San Mateo", "Dec 2025 -- Present",
  r"Research and development of Vision-Language-Action (VLA) and World Action Models (WAMs) for multi-embodiment robot control, toward generalist robot policies."),
 ("Sr. Research Scientist", "Meta AI Research", "Seattle", "Oct 2024 -- Dec 2025",
  r"Developed techniques for native image and video generation with large language models (LLMs)."),
 ("Postdoctoral Researcher", "Meta AI Research", "New York", "Jan 2023 -- Oct 2024",
  r"Developed generative AI techniques for \textbf{generation} (\href{https://ai.meta.com/research/movie-gen/}{Movie Gen}, \href{https://emu-video.metademolab.com/}{Emu Video}, \href{https://people.eecs.berkeley.edu/~xdwang/projects/InstDiff/}{InstanceDiffusion}) and \textbf{evaluation} (\href{https://arxiv.org/pdf/2311.10708.pdf}{\mbox{SelfEval}})."),
]
EDU = [
 ("PhD in Electrical Engineering", "University of Maryland, College Park", "Aug 2016 -- Dec 2022",
  ["Advisors: Rama Chellappa and Abhinav Shrivastava", "Thesis: Towards In-the-Wild Visual Understanding"]),
 ("Master's in Electrical Engineering", "University of Maryland, College Park", "Aug 2016 -- Dec 2021",
  ["Advisor: Rama Chellappa"]),
 ("Dual Degree in Electrical Engineering", "Indian Institute of Technology, Kharagpur", "Jun 2011 -- Jun 2016",
  ["Advisors: Pranab Kumar Datta and Rajeev Ranjan Sahay", "Thesis: Body Pose Classification using Deep Learning"]),
]
CVPR="Conference on Computer Vision and Pattern Recognition (CVPR)"
ICCV="International Conference on Computer Vision (ICCV)"
# (title, authors, full venue, short venue)
PUBS = [
 ("Toward Diffusible High-Dimensional Latent Spaces: A Frequency Perspective",
  r"Bolin Lai, Xudong Wang, \me, James M. Rehg, Zsolt Kira, Rohit Girdhar, Ishan Misra", CVPR+", 2026", "CVPR 2026"),
 ("Trokens: Semantic-Aware Relational Trajectory Tokens for Few-Shot Action Recognition",
  r"Pulkit Kumar, Shuaiyi Huang, Matthew Walmer, \me, Abhinav Shrivastava", ICCV+", 2025", "ICCV 2025"),
 ("MotiF: Making Text Count in Image Animation with Motion Focal Loss",
  r"Shijie Wang, Samaneh Azadi, Rohit Girdhar, \me, Chen Sun, Xi Yin", CVPR+", 2025", "CVPR 2025"),
 ("Diffusion Autoencoders are Scalable Image Tokenizers",
  r"Yinbo Chen, Rohit Girdhar, Xiaolong Wang, \me, Ishan Misra", "arXiv preprint arXiv:2501.18593, 2025", "arXiv:2501.18593, 2025"),
 ("Movie Gen: A Cast of Media Foundation Models",
  r"\textit{Meta Movie Gen team} --- Core contributor", "arXiv preprint arXiv:2410.13720, 2024", "arXiv:2410.13720, 2024"),
 ("Emu Video: Factorizing Text-to-Video Generation by Explicit Image Conditioning",
  r"Rohit Girdhar, Mannat Singh, Andrew Brown, Quentin Duval, Samaneh Azadi, \me, Mian Akbar Shah, Xi Yin, Devi Parikh, Ishan Misra",
  "European Conference on Computer Vision (ECCV), 2024", "ECCV 2024"),
 ("SelfEval: Leveraging the Discriminative Nature of Generative Models for Evaluation",
  r"\me, Ishan Misra", "Transactions on Machine Learning Research (TMLR), 2024", "TMLR 2024"),
 ("InstanceDiffusion: Instance-level Control for Image Generation",
  r"Xudong Wang, Trevor Darrell, \me, Rohit Girdhar, Ishan Misra", CVPR+", 2024", "CVPR 2024"),
 ("MOST: Multiple Object Localization with Self-Supervised Transformers for Object Discovery",
  r"\me, Ishan Misra, Rama Chellappa, Abhinav Shrivastava", ICCV+", 2023", "ICCV 2023"),
 ("SparseDet: Improving Sparsely Annotated Object Detection with Pseudo-positive Mining",
  r"\me$^{*}$, Saksham Suri$^{*}$, Rama Chellappa, Abhinav Shrivastava", ICCV+", 2023", "ICCV 2023"),
 ("An Empirical Analysis of Boosting Neural Networks",
  r"\me, Michael Jones, Rama Chellappa", "International Joint Conference on Neural Networks (IJCNN), 2022", "IJCNN 2022"),
 ("The Pursuit of Knowledge: Discovering and Localizing New Concepts using Dual Memory",
  r"\me, Rama Chellappa, Abhinav Shrivastava", ICCV+", 2021", "ICCV 2021"),
 ("Towards Discovery and Attribution of Open-world GAN Generated Images",
  r"Saksham Suri$^{*}$, Sharath Girish$^{*}$, \me, Abhinav Shrivastava", ICCV+", 2021", "ICCV 2021"),
 ("Detecting Human-Object Interactions using Functional Common-Sense",
  r"Ankan Bansal, \me, Abhinav Shrivastava, Rama Chellappa", "AAAI Conference on Artificial Intelligence (AAAI), 2020", "AAAI 2020"),
 ("A Dual-Path Model with Adaptive Attention for Vehicle Re-Identification",
  r"Pirazh Khorramshahi, Amit Kumar, Neehar Peri, \me, Jun-Cheng Chen, Rama Chellappa", ICCV+", 2019", "ICCV 2019"),
 ("Body Part Alignment and Temporal Attention for Video-Based Person Re-Identification",
  r"\me, Michael Jones", "British Machine Vision Conference (BMVC), 2019", "BMVC 2019"),
]
INTERN = [
 ("Cruise AI", "San Francisco", "2022", "Advisors: Dr. Xiao Zhang, Dr. Carl Vondrick",
  "Developed efficient algorithms for continual self-supervised learning."),
 ("Mitsubishi Electric Research Laboratory", "Boston", "2018, 2019", "Advisor: Dr. Mike Jones",
  "Worked on video-based person re-identification and ensembles of deep neural networks."),
]
AWARDS = [
 r"Awarded the \textbf{Ann G. Wylie Dissertation Fellowship} for the academic year 2021--22.",
 r"Selected for the A. James Clark School of Engineering \textbf{Future Faculty Cohort} for the academic year 2021--22.",
 r"Awarded the prestigious \textbf{George Corcoran Award} for excellence in teaching for the academic year 2017--18.",
 r"Awarded \textbf{Outstanding Teaching Assistant Award} for the academic year 2017--18.",
 r"Awarded \textbf{Outstanding Reviewer} for CVPR 2021 and NeurIPS 2023.",
 r"Awarded \textbf{Best Paper Award (Honorable Mention)} at ANTS 2016, Bangalore.",
]
REVIEW_CONF = r"CVPR ('19--'26), ECCV ('20--'26), ICCV ('19--'25), ICLR ('23--'25), NeurIPS ('23--'25), ICML ('24)"
REVIEW_JOUR = r"IJCV, T-PAMI, Pattern Recognition Letters"
