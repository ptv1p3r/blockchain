

# Dicas do source:
* *NOTA* Sempre que o novo capitulo (normal ou dos iniciais: agradecimentos, lista de ... ) não começar numa página impar é preciso meter o comando \LIMPA antes de começar essa secção.

* Só preicsam de mexer nos ficheiros .tex e .bib:
	* student_project_definitions.tex: contem as variáveis do aluno/projecto (ex: titulo, nomes, etc).
	* structure.tex: contem a estrutura do conteudo do projecto, isto é, os captiulos.
	* main.tex: só precisam de alterar se quiserem remover alguma das secções iniciais facultativa (i.e., agradecimentos) ou adicionar o comando \LIMPA caso estas secções não estejam a começar em página impar.
	* chapters/\*/\*.tex é onde vão escrever o vosso relatório. 
	* acronimos.tex onde vão escrever os acrónimos utilizados no documento

* Directorias: 
	* Raiz onde têm todos os ficheiros - inclusive o main.tex 

	* Em chapters têm os documentos que precisam editar:
		*	acks - agradecimentos
		*	abstract - resumo do trabalho 
		*	introduction - introdução
		*	quando precisarem de criar novos cappitulos, copiem a introduction para outra pasta que precisem, por exemplo: related work, conclusions, etc. Depois devem alterar o nome do ficheiro .tex aí dentro, o texto no início desse ficheiro (onde está o nome do capitulo \chapter{NOME} e adicionar uma linha:  \include{chapters/introduction/NOVA PASTA} por baixo de \include{chapters/introduction/introduction} no main.tex

	* Em images devem guardar todas as imagens que precisam no relatório. Podem organizar em sub-pastas desde que depois metam isso no path do comando de include (ver exemplo na introduction.tex).

	
* Referencias: 
	* Comecem por seguir o exemplo. Mas quando quiserem acrescentar um artigo de revista ou conferencia, facilmente encontram o bibtex nos motores de busca que falei nas aulas, tipo "Export as bibtex", aí ele vai gerar o código como está em Chapters/references/references.bib 

	* Também pode criar um bibtex para sites, artigos normais, etc. Há vários exemplos online, se precisarem de ajuda digam. 


# Dicas para usar:
* Apagar todos os \lipsum em introduction.tex , resumo.tex e agradecimentos.tex

