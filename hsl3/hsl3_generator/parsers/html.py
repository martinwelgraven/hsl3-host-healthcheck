import os

from hsl3.hsl3_generator.configs.dcls_module import ConfigModule
from hsl3.hsl3_generator.configs.dcls_project import ConfigProject
from html.parser import HTMLParser
import shutil


class HTMLfileParser(HTMLParser):
    """ Class for creating the HTML documentation file for a logic module. """

    def __init__(self):
        super().__init__()

        self.file_name = ""
        self.project_config: ConfigProject
        self.node_config: ConfigModule
        self.html_content = ""


    def init(self, project_config: ConfigProject, node_config: ConfigModule):
        self.project_config = project_config
        self.node_config = node_config
        

    def build_html(self):
        html_content = self._doctype()
        html_content += "<html>\n"
        html_content += "\t<head> \n"
        html_content += self._header()
        html_content += "\t</head>\n"
        html_content += "\t<body>\n"
        html_content += f"\t\t<div>\n"
        html_content += self._body_header()
        html_content += self._content()
        html_content += f"\t\t</div>\n"
        html_content += "\t</body>\n"
        html_content += "</html>\n"

        self.html_content = html_content

    def _doctype(self):
        doctype = 'html PUBLIC "-//W3C//DTD HTML 4.01//EN"'
        return f"<!DOCTYPE {doctype}>\n"

    def _header(self):
        html_content = "\t\t<link rel=\"stylesheet\" href=\"style.css\">\n"
        html_content += f"\t\t<title>Logic - {self.node_config.name}</title>\n"
        html_content += "\t\t<style>\n"
        html_content += "\t\t\tbody { background: none; }\n"
        html_content += "\t\t</style>\n"
        html_content += "\t\t<meta http-equiv=\"Content-Type\" content=\"text/html;charset=utf-8\">\n"
        return html_content

    
    def _body_header(self):
        html_content = f"\t\t\t<div class=\"top-title\">{self.node_config.name}</div>\n"
        html_content += "\t\t\t<div class=\"nav\"><a href=\"javascript:history.back()\">Previous</a> / \n"
        html_content += "\t\t\t\t<a href=\"javascript:history.forward()\">Next</a> | \n"
        html_content += "\t\t\t\t<a href=\"hlpsearch.html\">Search</a> | \n"
        html_content += "\t\t\t\t<a href=\"index.html\">Help</a> / \n"
        html_content += "\t\t\t\t<a href=\"logic.html\">Logic</a> / \n"
        html_content += f"\t\t\t\t{self.node_config.name}\n"
        html_content += "\t\t\t</div>\n"
        html_content += "\t\t\t<div class=\"index\">\n"
        html_content += "\t\t\t\t<div class=\"index-title\"><a id=\"doc_index_1_\"></a>Contents</div>\n"
        html_content += "\t\t\t\t<div class=\"t-line\">\n"
        html_content += "\t\t\t\t\t<div class=\"t-chapter\">\n"
        html_content += "\t\t\t\t\t\t<a href=\"#auto_index_anchor_1_\">1.</a>\n"
        html_content += "\t\t\t\t\t</div>\n"
        html_content += "\t\t\t\t\t<div class=\"t-text\">\n"
        html_content += "\t\t\t\t\t\t<a href=\"#auto_index_anchor_1_\">Description</a>\n"
        html_content += "\t\t\t\t\t</div>\n"
        html_content += "\t\t\t\t</div>\n"
        html_content += "\t\t\t\t<div class=\"t-line\">\n"
        html_content += "\t\t\t\t\t<div class=\"t-chapter\">\n"
        html_content += "\t\t\t\t\t\t<a href=\"#auto_index_anchor_2_\">2.</a>\n"
        html_content += "\t\t\t\t\t</div>\n"
        html_content += "\t\t\t\t\t<div class=\"t-text\">\n"
        html_content += "\t\t\t\t\t\t<a href=\"#auto_index_anchor_2_\">Inputs</a>\n"
        html_content += "\t\t\t\t\t</div>\n"
        html_content += "\t\t\t\t</div>\n"
        html_content += "\t\t\t\t<div class=\"t-line\">\n"
        html_content += "\t\t\t\t\t<div class=\"t-chapter\">\n"
        html_content += "\t\t\t\t\t\t<a href=\"#auto_index_anchor_3_\">3.</a>\n"
        html_content += "\t\t\t\t\t</div>\n"
        html_content += "\t\t\t\t\t<div class=\"t-text\">\n"
        html_content += "\t\t\t\t\t\t<a href=\"#auto_index_anchor_3_\">Outputs</a>\n"
        html_content += "\t\t\t\t\t</div>\n"
        html_content += "\t\t\t\t</div>\n"
        html_content += "\t\t\t\t<div class=\"t-line\">\n"
        html_content += "\t\t\t\t\t<div class=\"t-chapter\">\n"
        html_content += "\t\t\t\t\t\t<a href=\"#auto_index_anchor_4_\">4.</a>\n"
        html_content += "\t\t\t\t\t</div>\n"
        html_content += "\t\t\t\t\t<div class=\"t-text\">\n"
        html_content += "\t\t\t\t\t\t<a href=\"#auto_index_anchor_4_\">Other</a>\n"
        html_content += "\t\t\t\t\t</div>\n"
        html_content += "\t\t\t\t</div>\n"
        html_content += "\t\t\t\t<div class=\"t-line\">\n"
        html_content += "\t\t\t\t\t<div class=\"t-chapter\">\n"
        html_content += "\t\t\t\t\t\t<a href=\"#auto_index_anchor_5_\">5.</a>\n"
        html_content += "\t\t\t\t\t</div>\n"
        html_content += "\t\t\t\t\t<div class=\"t-text\">\n"
        html_content += "\t\t\t\t\t\t<a href=\"#auto_index_anchor_5_\">Similar functions</a>\n"
        html_content += "\t\t\t\t\t</div>\n"
        html_content += "\t\t\t\t</div>\n"
        html_content += "\t\t\t</div>\n"

        return html_content
                       
    def _content(self):
        html_content = "\t\t\t<div class=\"content\">\n"
        html_content += self._topic()
        html_content += self._inputs()
        html_content += self._outputs()
        html_content += self._other()
        html_content += "\t\t\t</div>\n"
    
        return html_content

    def _topic(self):
        html_content = "\t\t\t\t<div class=\"topic\">\n"
        html_content += self._description()
        html_content += self._warning() if self.node_config.warning != "" else ""
        html_content += self._note() if self.node_config.note != "" else ""
        html_content += "\t\t\t\t</div>\n"

        return html_content
    
    def _description(self):
        html_content = "\t\t\t\t\t<h2 class=\"t-line\">\n"
        html_content += "\t\t\t\t\t\t<a id=\"auto_index_anchor_1_\"></a>\n"
        html_content += "\t\t\t\t\t\t<span class=\"t-chapter\">1.</span>\n"
        html_content += "\t\t\t\t\t\t<span class=\"t-text\">Description</span>\n"
        html_content += "\t\t\t\t\t</h2>\n"
        html_content += f"\t\t\t\t\t<div class=\"descr\">{self.node_config.description}</div>\n"

        return html_content

    def _warning(self):
        html_content = "\t\t\t\t\t<div class=\"alert-box ibox-warning\">\n"
        html_content += "\t\t\t\t\t\t<div class=\"box-title\">Warning</div>\n"
        html_content += "\t\t\t\t\t\t<div class=\"box-text\">\n"
        html_content += f"\t\t\t\t\t\t\t<div class=\"descr\">{self.node_config.warning}</div>\n"
        html_content += "\t\t\t\t\t\t</div>\n"
        html_content += "\t\t\t\t\t</div>\n"

        return html_content if self.node_config.warning != None else ""

    def _note(self):
        html_content = "\t\t\t\t\t<div class=\"alert-box ibox-hint\">\n"
        html_content += "\t\t\t\t\t\t<div class=\"box-title\">Note</div>\n"
        html_content += "\t\t\t\t\t\t<div class=\"box-text\">\n"
        html_content += f"\t\t\t\t\t\t\t<div class=\"descr\">{self.node_config.note}</div>\n"
        html_content += "\t\t\t\t\t\t</div>\n"
        html_content += "\t\t\t\t\t</div>\n"

        return html_content if self.node_config.note != None else ""
    
    def _inputs(self):
        inputs_html = ""
        for input in self.node_config.inputs:
            inputs_html += self._input(input)

        html_content = "\t\t\t\t\t<h2 class=\"t-line\">\n"
        html_content += "\t\t\t\t\t\t<a id=\"auto_index_anchor_2_\"></a>\n"
        html_content += "\t\t\t\t\t\t<span class=\"t-chapter\">2.</span>\n"
        html_content += "\t\t\t\t\t\t<span class=\"t-text\">Inputs</span>\n"
        html_content += "\t\t\t\t\t</h2>\n"
        html_content += "\t\t\t\t\t<div>\n"
        html_content += "\t\t\t\t\t\t<table class=\"table-in\">\n"
        html_content += "\t\t\t\t\t\t\t<tr>\n"
        html_content += "\t\t\t\t\t\t\t\t<th class=\"io-nr center\">No.</th>\n"
        html_content += "\t\t\t\t\t\t\t\t<th class=\"io-name\">Name</th>\n"
        html_content += "\t\t\t\t\t\t\t\t<th class=\"io-init center\">Initialisation</th>\n"
        html_content += "\t\t\t\t\t\t\t\t<th class=\"io-descr\">Description</th>\n"
        html_content += "\t\t\t\t\t\t\t</tr>\n"
        html_content += inputs_html
        html_content += "\t\t\t\t\t\t</table>\n"
        html_content += "\t\t\t\t\t</div>\n"

        return html_content
            

    def _input(self, input):
        html_content = "\t\t\t\t\t\t\t<tr>\n"
        html_content += f"\t\t\t\t\t\t\t\t<td class=\"io-nr input center\">{input.index}</td>\n"
        html_content += f"\t\t\t\t\t\t\t\t<td class=\"io-name\">{input.label}</td>\n"
        html_content += f"\t\t\t\t\t\t\t\t<td class=\"io-init string center\">{input.init_value}</td>\n"
        html_content += "\t\t\t\t\t\t\t\t<td class=\"io-descr\">\n"
        html_content += f"\t\t\t\t\t\t\t\t<div class=\"descr\">{input.description}</div>\n"
        html_content += "\t\t\t\t\t\t\t\t</td>\n"
        html_content += "\t\t\t\t\t\t\t</tr>\n"

        return html_content
    
    def _outputs(self):
        outputs_html = ""
        for output in self.node_config.outputs:
            outputs_html += self._output(output)
        
        html_content = "\t\t\t\t\t<h2 class=\"t-line\">\n"
        html_content += "\t\t\t\t\t\t<a id=\"auto_index_anchor_3_\"></a>\n"
        html_content += "\t\t\t\t\t\t<span class=\"t-chapter\">3.</span>\n"
        html_content += "\t\t\t\t\t\t<span class=\"t-text\">Outputs</span>\n"
        html_content += "\t\t\t\t\t</h2>\n"
        html_content += "\t\t\t\t\t<div>\n"
        html_content += "\t\t\t\t\t\t<table class=\"table-out\">\n"
        html_content += "\t\t\t\t\t\t\t<tr>\n"
        html_content += "\t\t\t\t\t\t\t\t<th class=\"io-nr center\">No.</th>\n"
        html_content += "\t\t\t\t\t\t\t\t<th class=\"io-name\">Name</th>\n"
        html_content += "\t\t\t\t\t\t\t\t<th class=\"io-init center\">Initialisation</th>\n"
        html_content += "\t\t\t\t\t\t\t\t<th class=\"o-sbc center\"><a href=\"logic2.html#_Toc17193931\">SBC</a></th>\n"
        html_content += "\t\t\t\t\t\t\t\t<th class=\"io-descr\">Description</th>\n"
        html_content += "\t\t\t\t\t\t\t</tr>\n"
        html_content += outputs_html
        html_content += "\t\t\t\t\t\t</table>\n"
        html_content += "\t\t\t\t\t\t<div class=\"small\">\n"
        html_content += "\t\t\t\t\t\ts = <a href=\"logic2.html#_Toc17193931\">send</a>, \n"
        html_content += "\t\t\t\t\t\tsbc = <a href=\"logic2.html#_Toc17193931\">send by change</a>\n"
        html_content += "\t\t\t\t\t\t</div>\n"
        html_content += "\t\t\t\t\t</div>\n"

        return html_content

    def _output(self, output):
        html_content = "\t\t\t\t\t\t\t<tr>\n"
        html_content += f"\t\t\t\t\t\t\t\t<td class=\"io-nr output center\">{output.index}</td>\n"
        html_content += f"\t\t\t\t\t\t\t\t<td class=\"io-name\">{output.label}</td>\n"
        html_content += f"\t\t\t\t\t\t\t\t\t<td class=\"io-init string center\">{output.init_value}</td>\n"
        html_content += f"\t\t\t\t\t\t\t\t<td class=\"o-sbc center\">{output.sbc}</td>\n"
        html_content += "\t\t\t\t\t\t\t\t<td class=\"io-descr\">\n"
        html_content += f"\t\t\t\t\t\t\t\t\t<div class=\"descr\">{output.description}</div>\n"
        html_content += "\t\t\t\t\t\t\t\t</td>\n"
        html_content += "\t\t\t\t\t\t\t</tr>\n"

        return html_content

    def _other(self):
        html_content = "\t\t\t\t <h2 class=\"t-line\">\n"
        html_content += "\t\t\t\t\t<a id=\"auto_index_anchor_4_\"></a>\n"
        html_content += "\t\t\t\t\t<span class=\"t-chapter\">4.</span>\n"
        html_content += "\t\t\t\t\t<span class=\"t-text\">Other</span>\n"
        html_content += "\t\t\t\t</h2>\n"
        html_content += "\t\t\t\t<table class=\"table-logic-info\">\n"
        html_content += "\t\t\t\t\t<tr>\n"
        html_content += "\t\t\t\t\t\t<th>Internal designation:</th>\n"
        html_content += f"\t\t\t\t\t\t<td>{self.node_config.id}</td>\n"
        html_content += "\t\t\t\t\t</tr>\n"
        html_content += "\t\t\t\t\t<tr>\n"
        html_content += "\t\t\t\t\t\t<th>Category:</th>\n"
        html_content += f"\t\t\t\t\t\t<td>{self.node_config.category}</td>\n"
        html_content += "\t\t\t\t\t</tr>\n"
        html_content += "\t\t\t\t\t<tr>\n"
        html_content += "\t\t\t\t\t\t<th>Context:</th>\n"
        html_content += f"\t\t\t\t\t\t<td>{self.node_config.context}</td>\n"
        html_content += "\t\t\t\t\t</tr>\n"
        html_content += "\t\t\t\t</table>\n"

        return html_content

    def exists(self):
        self.file_name = os.path.join(self.project_config.source_path, self.project_config.html_file)
        return os.path.exists(self.file_name)
    
    def write_html(self):
        with open(self.file_name, 'w', encoding='utf-8') as f:
            f.write(self.html_content)

    def copy_css(self):
        css_source = os.path.join(self.project_config.root,'hsl3', 'css',  "style.css")
        
        if not os.path.exists(css_source):
            print(f"CSS file not found. Make sure that 'style.css' is located in the {os.sep}hsl3{os.sep}css{os.sep}  directory.")
        
        css_dest = os.path.join(self.project_config.source_path, "style.css")
        try:
            shutil.copyfile(css_source, css_dest)
        except Exception as e:
            print(f"Failed to copy CSS file: {e}")