A demonstrator for what a client to STAC parser pipeline might look like

Requires Java 1.7 or higher

    mvn initialize -X

Check the output above.  Are you using Java 1.7 or higher?

    mvn package
    irit-stac serve --port 7777
    time java -jar\
        target/stac-parser-client-0.1.jar\
        tcp://localhost:7777\
        ../parser/sample.soclog
