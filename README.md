# TCC_CNN_Garimpo_Amazonia

Repositório público do Trabalho de Conclusão de Curso intitulado "Detecção de Garimpo Ilegal na Amazônia Utilizando Visão Computacional e Redes Neurais Covolucionais" do Curso de Bacharelado em Ciência da Computação da PUC-SP

Por: Leonardo Fajardo Grupioni

Orientação: Profa. Dra. Edith Ranzini

Colaboração: Prof. Dr. Felipe Valencia de Almeida & Thomas Jean Georges Gallois

## Resumo:

O avanço do garimpo ilegal na Amazônia brasileira configura uma das principais ameaças à biodiversidade e às comunidades locais, exigindo mecanismos de monitoramento ágeis e escaláveis. Este trabalho propõe o desenvolvimento de um modelo de visão computacional baseado em Redes Neurais Convolucionais (CNNs) para a detecção automática de frentes de mineração em imagens de satélite. A metodologia utilizou a plataforma Google Earth Engine para a coleta e pré-processamento de dados, resultando na construção de um dataset balanceado com mais de 111 mil recortes de imagem, devidamente rotulados e curados para mitigar a interferência de nuvens. Para validar a abordagem, estabeleceu-se primeiramente um baseline com o algoritmo Random Forest, que atingiu um teto de acurácia de 72% e Área Sob a Curva (AUC) de 0,80, evidenciando as limitações de métodos baseados apenas em estatísticas de pixel. Em contrapartida, a implementação da arquitetura EfficientNet-B0, aliada a técnicas de Transferência de Aprendizado e Fine-Tuning, superou significativamente os modelos tradicionais, alcançando uma acurácia de 85,92% e uma AUC de 0,9371. Os resultados demonstram que o Aprendizado Profundo é capaz de extrair características espaciais complexas, distinguindo efetivamente cicatrizes de garimpo de outros alvos visuais ambíguos. Como contribuição à comunidade científica e ao suporte à fiscalização, todo o código-fonte desenvolvido e a metodologia de criação do conjunto de dados foram disponibilizados em repositório aberto, fomentando a reprodutibilidade e a continuidade das pesquisas no monitoramento do bioma amazônico.
