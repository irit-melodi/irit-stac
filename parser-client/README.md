A demonstrator for what a client to STAC parser pipeline might look like

mvn package
irit-stac serve --port 7777
time java -jar\
    target/stac-parser-client-0.1.jar\
    tcp://localhost:7777\
    ../parser/sample.soclog
