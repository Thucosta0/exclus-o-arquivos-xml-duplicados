# Aplicativo de Exclusão de Arquivos XML Duplicados

Este aplicativo foi desenvolvido para auxiliar na identificação e exclusão de arquivos XML duplicados em uma pasta, utilizando sufixos predefinidos ou personalizados.

## Funcionalidades

- **Seleção de Pasta**: Escolha a pasta onde estão os arquivos XML.
- **Gestão de Sufixos**: Adicione, remova ou detecte automaticamente sufixos de arquivos duplicados.
- **Análise de Arquivos**: Identifica arquivos XML duplicados com base nos sufixos cadastrados.
- **Exclusão de Duplicados**: Remove os arquivos duplicados após confirmação.

## Requisitos

- Python 3.6 ou superior
- Bibliotecas:
  - `customtkinter`
  - `pillow`
  - `pyinstaller` (para empacotamento)

## Instalação

1. Clone o repositório:
   ```sh
   git clone https://github.com/Thucosta0/exclus-o-arquivos-xml-duplicados.git
   cd exclus-o-arquivos-xml-duplicados
   ```

2. Instale as dependências:
   ```sh
   pip install customtkinter pillow pyinstaller
   ```

3. Execute o aplicativo:
   ```sh
   python app.py
   ```

## Empacotamento

Para empacotar o aplicativo em um executável (.exe) com imagens incluídas, siga os passos abaixo:

1. **Verifique os arquivos necessários**:
   - `app.py`
   - `logo.ico` (ícone do aplicativo)
   - `Sociedade_sem pilares.png` (logo da Sociedade)
   - `Logo centro de serviços einstein.png` (logo do Einstein)

2. **Empacote com PyInstaller**:
   No terminal, execute:
   ```sh
   pyinstaller --noconfirm --onefile --windowed --icon=logo.ico app.py --add-data "Sociedade_sem pilares.png;." --add-data "Logo centro de serviços einstein.png;."
   ```

3. **Encontre o executável**:
   O arquivo gerado estará em:
   ```
   dist/app.exe
   ```

4. **Teste o executável**:
   Abra o `app.exe` e verifique se as imagens aparecem corretamente.

## Uso

1. **Selecione a Pasta**: Clique em "Selecionar" e escolha a pasta com os arquivos XML.
2. **Gerencie Sufixos**: Use os botões "Adicionar Sufixo", "Remover Sufixo" ou "Detectar Sufixos" para configurar os sufixos.
3. **Analise Arquivos**: Clique em "Analisar Arquivos" para identificar duplicados.
4. **Exclua Duplicados**: Clique em "Excluir Duplicados" para remover os arquivos identificados.

## Contribuição

Contribuições são bem-vindas! Sinta-se à vontade para abrir issues ou enviar pull requests.

## Licença

Este projeto está licenciado sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## Contato

Para dúvidas ou sugestões, entre em contato através do e-mail: [arthur.bleck@einstein.br](mailto:arthur.bleck@einstein.br). 