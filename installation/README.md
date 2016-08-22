# PROMS Installation Instructions

1. Install prerequisites
    * see 'prerequisites.txt'

2. Install a triplestore with a RESTful SPARQL 1.1 interface
    * default is Apache Fuseki 2 (https://jena.apache.org/documentation/fuseki2/)
    * see install-fuseki.sh in subfolder. You may need to update the Fuseki file version extension (currently -2.4.0.tar.gz)

3. Clone PROMS
    * https://bitbucket.csiro.au/projects/EIS/repos/proms 
    * make sure to clone recursively (git clone --recursive {PROMS_REPO}) in order to retireve Git submodules such as that for the RuleSets

4. Configure settings.py
    * settings.py contains extensive documentation for each setting
    
5. Apply theme overlays
    * PROMS Server ships wuith the 'vanilla' theme out of the box
    * other themes are available which are Git modules containing instructions
    * see GA theme: https://github.com/nicholascar/proms-theme-ga
    * see CSIRO theme: https://bitbucket.csiro.au/projects/EIS/repos/proms-theme-csiro
    
6. Run PROMS
    * either as a stand-alone service using Python Flask's inbuilt webserver or as a WSGI module of another webserver (e.g. Apache) 
    * even if running as a standa-alone service, you will need an Apache or similar server in front of PROMS in order to proxy to the SPARQL endpoints
    * see install-apache.sh in subfolder
