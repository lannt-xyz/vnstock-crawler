import os
from enum import Enum

from jinja2 import Template


class PromptTemplate(Enum):
    COMPANY_PROFILE = "company_profile"
    MACRO_DATA = "macro_data"


class PromptLoader:
    def __init__(self, template_dir: str = None):
        """
        Initialize the PromptLoader with a template directory.

        Args:
            template_dir (str): Path to the directory containing prompt templates.
                               Defaults to 'app/prompts' relative to the project root.
        """
        if template_dir is None:
            # Default to app/prompts relative to the current file
            current_dir = os.path.dirname(os.path.abspath(__file__))
            template_dir = os.path.join(current_dir, "..", "prompts")
        self.template_dir = template_dir

    def load_template(self, template: PromptTemplate) -> Template:
        """
        Load a prompt template from a file.

        Args:
            template (PromptTemplate): Enum value representing the template file (e.g., PromptTemplate.COMPANY_PROFILE).

        Returns:
            Template: A Jinja2 Template object for the loaded template.

        Raises:
            FileNotFoundError: If the template file does not exist.
        """
        template_file = f"{template.value}.j2"
        template_path = os.path.join(self.template_dir, template_file)
        if not os.path.exists(template_path):
            raise FileNotFoundError(
                f"Template file '{template_file}' not found in '{self.template_dir}'"
            )

        with open(template_path, "r", encoding="utf-8") as file:
            template_content = file.read()

        return Template(template_content)

    def apply_template(self, template: PromptTemplate, **kwargs) -> str:
        """
        Load a template and apply substitutions using Jinja2.

        Args:
            template (PromptTemplate): Enum value representing the template file.
            **kwargs: Key-value pairs for substitution (e.g., company_text='some text').

        Returns:
            str: The formatted prompt with substitutions applied.

        Raises:
            FileNotFoundError: If the template file does not exist.
            UndefinedError: If a required variable is missing in kwargs.
        """
        template = self.load_template(template)
        try:
            return template.render(**kwargs)
        except Exception as e:
            raise RuntimeError(f"Error rendering template '{template}': {e}")
