import os
import re
import json
import customtkinter as ctk
from tkinter import filedialog, messagebox, simpledialog, PhotoImage
import glob
from PIL import Image, ImageTk
import base64
from io import BytesIO
import sys

# Logos em formato SVG (usado apenas se as imagens reais não estiverem disponíveis)
# Logo da Sociedade (azul com forma circular e texto interno)
SOCIEDADE_LOGO_SVG = '''
<svg xmlns="http://www.w3.org/2000/svg" width="120" height="120" viewBox="0 0 120 120">
  <circle cx="60" cy="60" r="55" fill="#1a73e8" />
  <circle cx="60" cy="60" r="45" fill="#fff" />
  <circle cx="60" cy="60" r="35" fill="#1a73e8" />
  <text x="60" y="65" font-family="Arial" font-size="20" font-weight="bold" text-anchor="middle" fill="white">SBS</text>
</svg>
'''

# Logo do Einstein (formato E estilizado em cores azuis)
EINSTEIN_LOGO_SVG = '''
<svg xmlns="http://www.w3.org/2000/svg" width="120" height="120" viewBox="0 0 120 120">
  <rect x="10" y="10" width="100" height="100" rx="10" fill="#0056b3" />
  <rect x="25" y="25" width="70" height="70" rx="5" fill="#fff" />
  <path d="M35 35 H85 V47 H50 V55 H75 V67 H50 V75 H85 V87 H35 Z" fill="#0056b3" />
</svg>
'''

def resource_path(relative_path):
    """Retorna o caminho absoluto, compatível com PyInstaller."""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# Caminhos para os arquivos de imagem
SOCIEDADE_LOGO_PATH = resource_path("Sociedade_sem pilares.png")
EINSTEIN_LOGO_PATH = resource_path("Logo centro de serviços einstein.png")

class ExclusaoArquivosApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Exclusão de Arquivos XML Duplicados")
        self.root.geometry("1100x790")
        self.root.resizable(False, False)
        
        # Definir ícone da janela a partir do arquivo .ico, se existir
        ico_path = os.path.join(os.path.dirname(__file__), "logo.ico")
        if os.path.exists(ico_path):
            try:
                self.root.iconbitmap(ico_path)
            except Exception as e:
                print(f"Erro ao definir o ícone .ico: {e}")
                self.set_window_icon()
        else:
            self.set_window_icon()
        
        # Configuração do tema
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")
        
        # Arquivo de banco de dados de sufixos
        self.db_file = "sufixos_duplicados.txt"
        self.sufixos = self.carregar_sufixos()
        
        # Carregar logos embutidas no código
        self.logo = None
        self.small_logo = None
        self.einstein_logo = None
        
        # Carregar logo da Sociedade (primeiro do arquivo, se não existir, usar SVG)
        try:
            # Primeiro tenta carregar do arquivo físico
            if os.path.exists(SOCIEDADE_LOGO_PATH):
                print(f"Carregando logo da Sociedade do arquivo: {SOCIEDADE_LOGO_PATH}")
                print(f"Caminho completo: {os.path.abspath(SOCIEDADE_LOGO_PATH)}")
                
                # Tentar abrir a imagem
                try:
                    sociedade_img = Image.open(SOCIEDADE_LOGO_PATH)
                except Exception as img_error:
                    print(f"Erro ao abrir imagem da Sociedade: {img_error}")
                    raise
                
                # Redimensionar mantendo a proporção
                basewidth = 120
                wpercent = (basewidth / float(sociedade_img.size[0]))
                hsize = int((float(sociedade_img.size[1]) * float(wpercent)))
                
                try:
                    sociedade_resized = sociedade_img.resize((basewidth, hsize), Image.Resampling.LANCZOS)
                except AttributeError:
                    # Fallback para versões mais antigas do Pillow
                    sociedade_resized = sociedade_img.resize((basewidth, hsize), Image.LANCZOS)
                
                # Criar imagem CTk
                self.logo = ctk.CTkImage(
                    light_image=sociedade_resized,
                    dark_image=sociedade_resized,
                    size=(basewidth, hsize)
                )
                print("Logo da Sociedade carregado com sucesso!")
            else:
                print(f"Arquivo de logo da Sociedade não encontrado: {SOCIEDADE_LOGO_PATH}")
                print(f"Diretório atual: {os.getcwd()}")
                print(f"Arquivos no diretório: {os.listdir('.')}")
                raise FileNotFoundError(f"Arquivo não encontrado: {SOCIEDADE_LOGO_PATH}")
                
        except Exception as e:
            print(f"Erro ao carregar logo da Sociedade do arquivo: {e}")
            print("Usando imagem de fallback para logo da Sociedade")
            # Fallback para SVG ou imagem gerada
            try:
                # Importar librsvg se disponível para renderizar SVG
                try:
                    import cairosvg
                    # Converter SVG para PNG usando cairosvg
                    png_bytes = cairosvg.svg2png(bytestring=SOCIEDADE_LOGO_SVG.encode('utf-8'))
                    sociedade_bytes_io = BytesIO(png_bytes)
                    sociedade_img = Image.open(sociedade_bytes_io)
                except ImportError:
                    # Fallback para imagem gerada se cairosvg não estiver disponível
                    sociedade_img = self.create_society_logo_image()
                
                # Redimensionar mantendo a proporção
                basewidth = 120
                wpercent = (basewidth / float(sociedade_img.size[0]))
                hsize = int((float(sociedade_img.size[1]) * float(wpercent)))
                
                try:
                    sociedade_resized = sociedade_img.resize((basewidth, hsize), Image.Resampling.LANCZOS)
                except AttributeError:
                    # Fallback para versões mais antigas do Pillow
                    sociedade_resized = sociedade_img.resize((basewidth, hsize), Image.LANCZOS)
                
                # Criar imagem CTk
                self.logo = ctk.CTkImage(
                    light_image=sociedade_resized,
                    dark_image=sociedade_resized,
                    size=(basewidth, hsize)
                )
            except Exception as e:
                print(f"Erro ao criar logo da Sociedade alternativo: {e}")
                # Último recurso: criar um placeholder de imagem azul com SBS
                self.logo = self.create_text_logo("SBS", "#1a73e8")
        
        # Carregar logo do Einstein (primeiro do arquivo, se não existir, usar SVG)
        try:
            # Primeiro tenta carregar do arquivo físico
            if os.path.exists(EINSTEIN_LOGO_PATH):
                print(f"Carregando logo do Einstein do arquivo: {EINSTEIN_LOGO_PATH}")
                print(f"Caminho completo: {os.path.abspath(EINSTEIN_LOGO_PATH)}")
                
                # Tentar abrir a imagem
                try:
                    einstein_img = Image.open(EINSTEIN_LOGO_PATH)
                except Exception as img_error:
                    print(f"Erro ao abrir imagem do Einstein: {img_error}")
                    raise
                
                # Redimensionar mantendo a proporção
                bottom_width = 120
                wpercent = (bottom_width / float(einstein_img.size[0]))
                bottom_height = int((float(einstein_img.size[1]) * float(wpercent)))
                
                try:
                    einstein_resized = einstein_img.resize((bottom_width, bottom_height), Image.Resampling.LANCZOS)
                except AttributeError:
                    # Fallback para versões mais antigas do Pillow
                    einstein_resized = einstein_img.resize((bottom_width, bottom_height), Image.LANCZOS)
                
                # Criar imagem CTk
                self.einstein_logo = ctk.CTkImage(
                    light_image=einstein_resized,
                    dark_image=einstein_resized,
                    size=(bottom_width, bottom_height)
                )
                print("Logo do Einstein carregado com sucesso!")
            else:
                print(f"Arquivo de logo do Einstein não encontrado: {EINSTEIN_LOGO_PATH}")
                print(f"Diretório atual: {os.getcwd()}")
                print(f"Arquivos no diretório: {os.listdir('.')}")
                raise FileNotFoundError(f"Arquivo não encontrado: {EINSTEIN_LOGO_PATH}")
        except Exception as e:
            print(f"Erro ao carregar logo do Einstein do arquivo: {e}")
            print("Usando imagem de fallback para logo do Einstein")
            # Fallback para SVG ou imagem gerada
            try:
                # Importar librsvg se disponível para renderizar SVG
                try:
                    import cairosvg
                    # Converter SVG para PNG usando cairosvg
                    png_bytes = cairosvg.svg2png(bytestring=EINSTEIN_LOGO_SVG.encode('utf-8'))
                    einstein_bytes_io = BytesIO(png_bytes)
                    einstein_img = Image.open(einstein_bytes_io)
                except ImportError:
                    # Fallback para imagem gerada se cairosvg não estiver disponível
                    einstein_img = self.create_einstein_logo_image()
                    
                # Redimensionar mantendo a proporção
                bottom_width = 120
                wpercent = (bottom_width / float(einstein_img.size[0]))
                bottom_height = int((float(einstein_img.size[1]) * float(wpercent)))
                
                try:
                    einstein_resized = einstein_img.resize((bottom_width, bottom_height), Image.Resampling.LANCZOS)
                except AttributeError:
                    # Fallback para versões mais antigas do Pillow
                    einstein_resized = einstein_img.resize((bottom_width, bottom_height), Image.LANCZOS)
                
                # Criar imagem CTk
                self.einstein_logo = ctk.CTkImage(
                    light_image=einstein_resized,
                    dark_image=einstein_resized,
                    size=(bottom_width, bottom_height)
                )
            except Exception as e:
                print(f"Erro ao criar logo do Einstein alternativo: {e}")
                # Último recurso: criar um placeholder de imagem azul com "HSE"
                self.einstein_logo = self.create_text_logo("HSE", "#0056b3")
        
        # Frame principal
        self.frame = ctk.CTkFrame(self.root)
        self.frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Frame para logo e título
        self.header_frame = ctk.CTkFrame(self.frame)
        self.header_frame.pack(fill="x", padx=10, pady=10)
        
        # Criar três colunas no header_frame para centralizar o título
        self.header_frame.columnconfigure(0, weight=1)  # Coluna esquerda (logo)
        self.header_frame.columnconfigure(1, weight=10)  # Coluna central (título)
        self.header_frame.columnconfigure(2, weight=1)  # Coluna direita (espaço vazio)
        
        # Exibindo a logo na coluna esquerda (se foi carregada)
        if self.logo:
            self.logo_label = ctk.CTkLabel(self.header_frame, image=self.logo, text="")
            self.logo_label.grid(row=0, column=0, padx=(10, 0), pady=10, sticky="w")
        
        # Título centralizado na coluna do meio
        self.title_label = ctk.CTkLabel(
            self.header_frame, 
            text="Exclusão de Arquivos XML Duplicados",
            font=("Roboto", 20, "bold")
        )
        self.title_label.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        
        # Frame para seleção de pasta
        self.folder_frame = ctk.CTkFrame(self.frame)
        self.folder_frame.pack(fill="x", padx=10, pady=10)
        
        # Entrada para o caminho da pasta
        self.path_entry = ctk.CTkEntry(
            self.folder_frame, 
            placeholder_text="Caminho da pasta com arquivos XML",
            width=400
        )
        self.path_entry.pack(side="left", padx=(0, 10), fill="x", expand=True)
        
        # Botão para selecionar pasta
        self.browse_button = ctk.CTkButton(
            self.folder_frame,
            text="Selecionar",
            command=self.browse_folder
        )
        self.browse_button.pack(side="right")
        
        # Frame para os sufixos
        self.sufixos_frame = ctk.CTkFrame(self.frame)
        self.sufixos_frame.pack(fill="x", padx=10, pady=10)
        
        # Label para os sufixos
        self.sufixos_label = ctk.CTkLabel(
            self.sufixos_frame,
            text=f"Sufixos de arquivos duplicados: {', '.join(self.sufixos) if self.sufixos else 'Nenhum sufixo cadastrado'}"
        )
        self.sufixos_label.pack(side="left", fill="x", expand=True)
        
        # Botões para gestão de sufixos
        self.add_sufixo_button = ctk.CTkButton(
            self.sufixos_frame,
            text="Adicionar Sufixo",
            command=self.adicionar_sufixo,
            width=120
        )
        self.add_sufixo_button.pack(side="right", padx=5)
        
        self.remove_sufixo_button = ctk.CTkButton(
            self.sufixos_frame,
            text="Remover Sufixo",
            command=self.remover_sufixo,
            width=120
        )
        self.remove_sufixo_button.pack(side="right", padx=5)

        self.detect_sufixo_button = ctk.CTkButton(
            self.sufixos_frame,
            text="Detectar Sufixos",
            command=self.detectar_sufixos,
            width=120
        )
        self.detect_sufixo_button.pack(side="right", padx=5)
        
        # Área de informações
        self.info_frame = ctk.CTkFrame(self.frame)
        self.info_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Texto para mostrar informações
        self.info_text = ctk.CTkTextbox(self.info_frame, height=300)
        self.info_text.pack(fill="both", expand=True, padx=10, pady=10)
        self.info_text.insert("1.0", "Selecione uma pasta para analisar os arquivos XML duplicados.\n")
        self.info_text.configure(state="disabled")
        
        # Botões de ação - usando grid para controle preciso do posicionamento
        self.buttons_frame = ctk.CTkFrame(self.frame)
        self.buttons_frame.pack(fill="x", padx=10, pady=10)
        
        # Configurar 3 colunas com pesos para centralizar
        self.buttons_frame.columnconfigure(0, weight=1)  # Botão de análise
        self.buttons_frame.columnconfigure(1, weight=1)  # Logo central
        self.buttons_frame.columnconfigure(2, weight=1)  # Botão de exclusão
        
        # Botão de análise à esquerda
        self.analyze_button = ctk.CTkButton(
            self.buttons_frame,
            text="Analisar Arquivos",
            command=self.analyze_files,
            height=35
        )
        self.analyze_button.grid(row=0, column=0, padx=20, pady=10, sticky="ew")
        
        # Logo Einstein no centro inferior
        if self.einstein_logo:
            self.footer_logo_label = ctk.CTkLabel(
                self.buttons_frame, 
                image=self.einstein_logo, 
                text=""
            )
            self.footer_logo_label.grid(row=0, column=1, padx=10, pady=10)
        
        # Botão de exclusão à direita
        self.delete_button = ctk.CTkButton(
            self.buttons_frame,
            text="Excluir Duplicados",
            command=self.delete_files,
            fg_color="#D22B2B",
            hover_color="#BB0000",
            height=35
        )
        self.delete_button.grid(row=0, column=2, padx=20, pady=10, sticky="ew")
        
        # Armazenar arquivos encontrados
        self.xml_files = []
        self.files_to_delete = []
        
        # Adicionar label de copyright no rodapé, centralizado
        self.copyright_label = ctk.CTkLabel(
            self.frame,
            text="Powered by ThTweaks\n© ThTweaks 2025",
            font=("Roboto", 12, "italic"),
            text_color="#888888"
        )
        self.copyright_label.pack(side="bottom", pady=(0, 5))

    def create_text_logo(self, text, color="#1a73e8"):
        """Cria uma imagem com texto como logo de fallback"""
        img = Image.new('RGB', (120, 120), color=color)
        # Tenta importar o módulo ImageDraw para desenhar texto
        try:
            from PIL import ImageDraw, ImageFont
            draw = ImageDraw.Draw(img)
            # Tenta usar uma fonte padrão
            try:
                font = ImageFont.truetype("arial.ttf", 40)
            except:
                font = ImageFont.load_default()
            
            # Centraliza o texto
            w, h = draw.textsize(text, font=font) if hasattr(draw, 'textsize') else (40, 40)
            draw.text(((120-w)/2, (120-h)/2), text, fill="white", font=font)
        except:
            # Se não puder desenhar texto, apenas retorna a imagem colorida
            pass
        
        return img
        
    def create_society_logo_image(self):
        """Cria uma imagem que simula a logo da Sociedade"""
        img = Image.new('RGB', (120, 120), color="white")
        try:
            from PIL import ImageDraw
            draw = ImageDraw.Draw(img)
            
            # Desenha círculos concêntricos
            draw.ellipse((10, 10, 110, 110), fill="#1a73e8")
            draw.ellipse((25, 25, 95, 95), fill="white")
            draw.ellipse((40, 40, 80, 80), fill="#1a73e8")
            
            # Tenta adicionar texto
            try:
                from PIL import ImageFont
                try:
                    font = ImageFont.truetype("arial.ttf", 20)
                except:
                    font = ImageFont.load_default()
                
                # Centraliza o texto "SBS"
                text = "SBS"
                w, h = draw.textsize(text, font=font) if hasattr(draw, 'textsize') else (30, 20)
                draw.text(((120-w)/2, (120-h)/2), text, fill="white", font=font)
            except:
                pass
        except:
            pass
        
        return img
        
    def create_einstein_logo_image(self):
        """Cria uma imagem que simula a logo do Einstein"""
        img = Image.new('RGB', (120, 120), color="#0056b3")
        try:
            from PIL import ImageDraw
            draw = ImageDraw.Draw(img)
            
            # Desenha retângulo interno
            draw.rectangle((20, 20, 100, 100), fill="white")
            
            # Desenha um "E" estilizado
            draw.rectangle((30, 35, 90, 45), fill="#0056b3")  # Topo do E
            draw.rectangle((30, 55, 75, 65), fill="#0056b3")  # Meio do E
            draw.rectangle((30, 75, 90, 85), fill="#0056b3")  # Base do E
            draw.rectangle((30, 35, 40, 85), fill="#0056b3")  # Linha vertical do E
        except:
            pass
        
        return img

    def carregar_sufixos(self):
        """Carrega os sufixos do arquivo de banco de dados"""
        if os.path.exists(self.db_file):
            try:
                with open(self.db_file, "r") as f:
                    return [line.strip() for line in f if line.strip()]
            except Exception as e:
                print(f"Erro ao carregar sufixos: {e}")
                return []
        else:
            # Criar arquivo com sufixos padrão se não existir
            sufixos_padrao = ["-110110.xml", "-210210.xml", "-110111.xml", "-210200.xml", "-210220.xml", "-210240.xml"]
            try:
                with open(self.db_file, "w") as f:
                    for sufixo in sufixos_padrao:
                        f.write(f"{sufixo}\n")
                return sufixos_padrao
            except Exception as e:
                print(f"Erro ao criar arquivo de sufixos: {e}")
                return sufixos_padrao
    
    def salvar_sufixos(self):
        """Salva os sufixos no arquivo de banco de dados"""
        try:
            with open(self.db_file, "w") as f:
                for sufixo in self.sufixos:
                    f.write(f"{sufixo}\n")
        except Exception as e:
            print(f"Erro ao salvar sufixos: {e}")
            messagebox.showerror("Erro", f"Erro ao salvar sufixos: {e}")

    def atualizar_label_sufixos(self):
        """Atualiza o label que mostra os sufixos cadastrados"""
        texto = f"Sufixos de arquivos duplicados: {', '.join(self.sufixos) if self.sufixos else 'Nenhum sufixo cadastrado'}"
        self.sufixos_label.configure(text=texto)

    def detectar_sufixos(self):
        """Detecta padrões de sufixos nos arquivos XML da pasta selecionada"""
        folder_path = self.path_entry.get()
        if not folder_path or not os.path.isdir(folder_path):
            messagebox.showerror("Erro", "Selecione uma pasta válida primeiro.")
            return
            
        # Buscar por arquivos XML na pasta
        xml_files = glob.glob(os.path.join(folder_path, "*.xml"))
        if not xml_files:
            messagebox.showinfo("Aviso", "Não foram encontrados arquivos XML na pasta selecionada.")
            return
            
        # Analisar nomes de arquivos para identificar padrões de sufixos
        file_names = [os.path.basename(f) for f in xml_files]
        
        # Tentar detectar padrões usando expressões regulares
        # Buscar por padrões como -NNNNNN.xml, onde N são dígitos
        sufixos_encontrados = set()
        padrao = re.compile(r'(.+?)(-\d+\.xml)$')
        
        # Dicionário para agrupar arquivos por nome base
        arquivos_agrupados = {}
        
        for nome in file_names:
            match = padrao.match(nome)
            if match:
                nome_base = match.group(1)
                sufixo = match.group(2)
                
                if nome_base not in arquivos_agrupados:
                    arquivos_agrupados[nome_base] = []
                
                arquivos_agrupados[nome_base].append(sufixo)
        
        # Para cada grupo com mais de um arquivo, identificar sufixos potenciais
        for nome_base, sufixos in arquivos_agrupados.items():
            if len(sufixos) > 1:
                sufixos_encontrados.update(sufixos)
        
        # Atualizar a lista de sufixos
        if sufixos_encontrados:
            # Perguntar ao usuário quais sufixos ele deseja adicionar
            sufixos_window = ctk.CTkToplevel(self.root)
            sufixos_window.title("Sufixos Detectados")
            sufixos_window.geometry("500x400")
            sufixos_window.grab_set()  # Modal
            
            # Label de instrução
            label = ctk.CTkLabel(sufixos_window, text="Selecione os sufixos a serem adicionados:")
            label.pack(pady=10)
            
            # Frame para checkboxes
            check_frame = ctk.CTkScrollableFrame(sufixos_window)
            check_frame.pack(fill="both", expand=True, padx=10, pady=10)
            
            # Variáveis para as checkboxes
            vars_sufixos = {}
            checkboxes = []
            
            for sufixo in sorted(sufixos_encontrados):
                var = ctk.BooleanVar(value=False)
                vars_sufixos[sufixo] = var
                checkbox = ctk.CTkCheckBox(check_frame, text=sufixo, variable=var)
                checkbox.pack(anchor="w", pady=5)
                checkboxes.append(checkbox)
            
            # Botão para confirmar adição
            def confirmar_adicao():
                novos_sufixos = []
                for sufixo, var in vars_sufixos.items():
                    if var.get():
                        if sufixo not in self.sufixos:
                            self.sufixos.append(sufixo)
                            novos_sufixos.append(sufixo)
                
                if novos_sufixos:
                    self.salvar_sufixos()
                    self.atualizar_label_sufixos()
                    mensagem = f"Sufixos adicionados: {', '.join(novos_sufixos)}"
                    messagebox.showinfo("Sucesso", mensagem)
                else:
                    messagebox.showinfo("Aviso", "Nenhum sufixo novo foi adicionado.")
                sufixos_window.destroy()
            
            # Botão para confirmar adição
            confirmar_button = ctk.CTkButton(
                sufixos_window,
                text="Adicionar Selecionados",
                command=confirmar_adicao
            )
            confirmar_button.pack(pady=10)
        else:
            messagebox.showinfo("Aviso", "Não foi possível detectar padrões de sufixos nos arquivos.")

    def adicionar_sufixo(self):
        """Adiciona um novo sufixo à lista de sufixos"""
        novo_sufixo = simpledialog.askstring("Adicionar Sufixo", "Digite o sufixo para arquivos duplicados (ex: -duplicado.xml):")
        if novo_sufixo:
            # Garantir que o sufixo tenha a extensão .xml
            if not novo_sufixo.endswith(".xml"):
                novo_sufixo += ".xml"
            
            # Adicionar o sufixo se ainda não existir
            if novo_sufixo not in self.sufixos:
                self.sufixos.append(novo_sufixo)
                self.salvar_sufixos()
                self.atualizar_label_sufixos()
                messagebox.showinfo("Sucesso", f"Sufixo '{novo_sufixo}' adicionado com sucesso!")
            else:
                messagebox.showinfo("Aviso", f"O sufixo '{novo_sufixo}' já existe na lista.")

    def remover_sufixo(self):
        """Remove um sufixo da lista de sufixos"""
        if not self.sufixos:
            messagebox.showinfo("Aviso", "Não há sufixos para remover.")
            return
            
        # Criar uma janela para selecionar o sufixo a ser removido
        remover_window = ctk.CTkToplevel(self.root)
        remover_window.title("Remover Sufixo")
        remover_window.geometry("400x300")
        remover_window.grab_set()  # Modal
        
        # Label de instrução
        label = ctk.CTkLabel(remover_window, text="Selecione o sufixo a ser removido:")
        label.pack(pady=10)
        
        # Frame para listbox e scrollbar
        list_frame = ctk.CTkFrame(remover_window)
        list_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Listbox para exibir os sufixos (usando Tkinter padrão porque CTk não tem listbox)
        import tkinter as tk
        listbox = tk.Listbox(list_frame)
        listbox.pack(side="left", fill="both", expand=True)
        
        # Scrollbar
        scrollbar = tk.Scrollbar(list_frame, orient="vertical")
        scrollbar.config(command=listbox.yview)
        scrollbar.pack(side="right", fill="y")
        listbox.config(yscrollcommand=scrollbar.set)
        
        # Preencher a listbox com os sufixos
        for sufixo in self.sufixos:
            listbox.insert(tk.END, sufixo)
            
        # Botão para confirmar remoção
        def confirmar_remocao():
            selecionados = listbox.curselection()
            if selecionados:
                index = selecionados[0]
                sufixo_remover = self.sufixos[index]
                self.sufixos.pop(index)
                self.salvar_sufixos()
                self.atualizar_label_sufixos()
                messagebox.showinfo("Sucesso", f"Sufixo '{sufixo_remover}' removido com sucesso!")
                remover_window.destroy()
            else:
                messagebox.showwarning("Aviso", "Selecione um sufixo para remover.")
        
        # Botão para confirmar remoção
        confirmar_button = ctk.CTkButton(
            remover_window,
            text="Remover",
            command=confirmar_remocao
        )
        confirmar_button.pack(pady=10)

    def browse_folder(self):
        """Abre um diálogo para selecionar a pasta com os arquivos XML"""
        folder = filedialog.askdirectory()
        if folder:
            self.path_entry.delete(0, "end")
            self.path_entry.insert(0, folder)

    def analyze_files(self):
        """Analisa os arquivos XML da pasta selecionada"""
        folder_path = self.path_entry.get()
        if not folder_path or not os.path.isdir(folder_path):
            messagebox.showerror("Erro", "Selecione uma pasta válida primeiro.")
            return
            
        if not self.sufixos:
            messagebox.showwarning("Aviso", "Não há sufixos cadastrados. Adicione sufixos para identificar arquivos duplicados.")
            return
            
        # Limpar dados anteriores
        self.xml_files = []
        self.files_to_delete = []
        
        # Habilitar a edição do texto info
        self.info_text.configure(state="normal")
        self.info_text.delete("1.0", "end")
        
        # Buscar por arquivos XML na pasta
        self.xml_files = glob.glob(os.path.join(folder_path, "*.xml"))
        
        if not self.xml_files:
            self.info_text.insert("end", "Não foram encontrados arquivos XML na pasta selecionada.")
            self.info_text.configure(state="disabled")
            return
            
        # Identificar arquivos para exclusão (que terminam com algum dos sufixos)
        self.files_to_delete = [f for f in self.xml_files if any(f.endswith(suffix) for suffix in self.sufixos)]
        
        # Exibir informações
        self.info_text.insert("end", f"Total de arquivos XML encontrados: {len(self.xml_files)}\n")
        self.info_text.insert("end", f"Arquivos identificados para exclusão: {len(self.files_to_delete)}\n\n")
        
        # Listar todos os arquivos, marcando os que serão excluídos
        self.info_text.insert("end", "Lista de arquivos XML:\n")
        
        for xml_file in sorted(self.xml_files):
            file_name = os.path.basename(xml_file)
            if xml_file in self.files_to_delete:
                self.info_text.insert("end", f"[SERÁ EXCLUÍDO] {file_name}\n")
            else:
                self.info_text.insert("end", f"{file_name}\n")
        
        self.info_text.configure(state="disabled")

    def delete_files(self):
        """Exclui os arquivos duplicados"""
        if not self.files_to_delete:
            messagebox.showinfo("Aviso", "Não há arquivos para excluir. Execute a análise primeiro.")
            return
            
        # Confirmar exclusão
        resposta = messagebox.askyesno(
            "Confirmar Exclusão", 
            f"Tem certeza que deseja excluir {len(self.files_to_delete)} arquivos duplicados?"
        )
        
        if not resposta:
            return
            
        # Excluir arquivos
        excluidos = 0
        erros = 0
        
        for arquivo in self.files_to_delete:
            try:
                os.remove(arquivo)
                excluidos += 1
            except Exception as e:
                print(f"Erro ao excluir {arquivo}: {e}")
                erros += 1
                
        # Exibir resultados
        self.info_text.configure(state="normal")
        self.info_text.insert("end", f"\n--- RESULTADO DA EXCLUSÃO ---\n")
        self.info_text.insert("end", f"Arquivos excluídos com sucesso: {excluidos}\n")
        
        if erros > 0:
            self.info_text.insert("end", f"Erros ao excluir: {erros}\n")
            
        self.info_text.configure(state="disabled")
        
        # Mensagem de conclusão
        if erros == 0:
            messagebox.showinfo("Sucesso", f"{excluidos} arquivos duplicados foram excluídos com sucesso!")
        else:
            messagebox.showwarning("Atenção", f"{excluidos} arquivos foram excluídos, mas ocorreram {erros} erros. Verifique o log.")
            
        # Atualizar a análise
        self.analyze_files()

    def set_window_icon(self):
        """Define o ícone da janela como uma imagem azul com 'XML' gerada via código, embutida."""
        try:
            from PIL import ImageDraw, ImageFont
            icon_img = Image.new('RGBA', (64, 64), color="#1a73e8")
            draw = ImageDraw.Draw(icon_img)
            try:
                font = ImageFont.truetype("arial.ttf", 24)
            except:
                font = ImageFont.load_default()
            text = "XML"
            w, h = draw.textsize(text, font=font) if hasattr(draw, 'textsize') else (32, 16)
            draw.text(((64-w)/2, (64-h)/2), text, fill="white", font=font)
            # Para Windows, usar iconphoto (funciona com PNG)
            icon_img = icon_img.resize((32, 32))
            icon = ImageTk.PhotoImage(icon_img)
            self.root.iconphoto(True, icon)
        except Exception as e:
            print(f"Não foi possível definir o ícone da janela: {e}")
            # Não faz nada se falhar

def main():
    """Função principal para executar o aplicativo"""
    root = ctk.CTk()
    app = ExclusaoArquivosApp(root)
    root.mainloop()


if __name__ == "__main__":
    main() 