graph TB
    subgraph "RCA完整链条"
        A[故障检测/告警] --> B[数据收集]
        B --> C[数据预处理]
        C --> D[异常定位]
        D --> E[根因分析]
        E --> F[解决方案制定]
        F --> G[故障修复实施]
        G --> H[知识积累]
    end

    subgraph "基于代理的LLM"
        RC1[RCAgent系统]
        RC2["观察快照键(OBSK)技术"]
        RC3["思考-行动-观察循环"]
        RC4["专家代理(代码/日志分析)"]
        RC5["轨迹级自一致性(TSC)"]
        RC6["JSON修复与错误处理"]
        RC7["本地部署Vicuna-13B"]
    end

    subgraph "检索增强的LLM"
        RCA1[RCACopilot]
        RCA2["自适应事件处理工作流"]
        RCA3["多源数据智能整合"]
        RCA4["时间敏感的相似性计算"]
        RCA5["思维链(CoT)推理"]
        RCA6["FastText嵌入技术"]
        
        PACE1["PACE框架"]
        PACE2["置信度评估机制"]
        PACE3["GPT-4增强提示模板"]
    end

    subgraph "基于微调的LLM"
        CRM1[Cloud_Root_Mitigation]
        CRM2["LoRA高效微调"]
        CRM3["大规模事件数据(40K+)"]
        CRM4["根因-缓解步骤联合训练"]
        CRM5["人工评估验证模板"]
        CRM6["多模态指标评估"]
    end

    subgraph "零样本与少样本的LLM"
        MAPE1[MAPE-K框架]
        MAPE2["少量样本学习"]
        MAPE3["Ansible Playbook生成"]
        MAPE4["功能正确性(FC)评估"]
        MAPE5["温度参数优化(T=0.6)"]
        MAPE6["多环境泛化验证"]
    end

    subgraph "概率推理与历史数据结合"
        LMTA1["LMTA框架"]
        LMTA2["历史数据概率推理"]
        LMTA3["故障模式知识库"]
        LMTA4["贝叶斯推理增强"]
    end

    %% 将研究连接到RCA链条对应环节
    B ---|"数据收集创新"| RC1
    B ---|"智能数据收集决策"| RC3
    
    C ---|"数据预处理创新"| RC2
    C ---|"日志预处理"| RC4
    C ---|"多源数据整合"| RCA3
    
    D ---|"异常定位创新"| RCA1
    D ---|"自适应事件处理"| RCA2
    D ---|"时间敏感匹配"| RCA4
    D ---|"专家代理分析"| RC4
    
    E ---|"根因分析创新"| RC1
    E ---|"结果一致性保障"| RC5
    E ---|"CoT推理"| RCA5
    E ---|"置信度评估"| PACE2
    E ---|"增强提示模板"| PACE3
    E ---|"微调LLM"| CRM1
    E ---|"LoRA优化"| CRM2
    E ---|"大规模训练"| CRM3
    E ---|"历史数据推理"| LMTA2
    E ---|"贝叶斯推理"| LMTA4
    
    F ---|"解决方案制定创新"| CRM1
    F ---|"根因-缓解联合"| CRM4
    F ---|"多指标评估"| CRM6
    F ---|"少量样本优化"| MAPE2
    F ---|"Ansible生成"| MAPE3
    
    G ---|"故障修复创新"| MAPE1
    G ---|"自动化脚本执行"| MAPE3
    G ---|"多环境适应"| MAPE6
    
    H ---|"知识积累创新"| RCA4
    H ---|"故障模式库"| LMTA3

    %% 技术细节连接
    RC1 --> RC2
    RC1 --> RC3
    RC1 --> RC4
    RC1 --> RC5
    RC1 --> RC6
    RC1 --> RC7
    
    RCA1 --> RCA2
    RCA1 --> RCA3
    RCA1 --> RCA4
    RCA1 --> RCA5
    RCA1 --> RCA6
    
    PACE1 --> PACE2
    PACE1 --> PACE3
    
    CRM1 --> CRM2
    CRM1 --> CRM3
    CRM1 --> CRM4
    CRM1 --> CRM5
    CRM1 --> CRM6
    
    MAPE1 --> MAPE2
    MAPE1 --> MAPE3
    MAPE1 --> MAPE4
    MAPE1 --> MAPE5
    MAPE1 --> MAPE6
    
    LMTA1 --> LMTA2
    LMTA1 --> LMTA3
    LMTA1 --> LMTA4

    classDef chain fill:#f9f,stroke:#333,stroke-width:2px;
    classDef rcagent fill:#bbf,stroke:#33f,stroke-width:1px;
    classDef rcacopilot fill:#bfb,stroke:#3f3,stroke-width:1px;
    classDef cloudroot fill:#fbb,stroke:#f33,stroke-width:1px;
    classDef mapek fill:#ffb,stroke:#ff3,stroke-width:1px;
    classDef lmta fill:#bff,stroke:#3ff,stroke-width:1px;
    
    class A,B,C,D,E,F,G,H chain;
    class RC1,RC2,RC3,RC4,RC5,RC6,RC7 rcagent;
    class RCA1,RCA2,RCA3,RCA4,RCA5,RCA6,PACE1,PACE2,PACE3 rcacopilot;
    class CRM1,CRM2,CRM3,CRM4,CRM5,CRM6 cloudroot;
    class MAPE1,MAPE2,MAPE3,MAPE4,MAPE5,MAPE6 mapek;
    class LMTA1,LMTA2,LMTA3,LMTA4 lmta;