package fr.irit.stac.client;

import org.zeromq.ZMQ;

import java.io.IOException;
import java.nio.file.FileSystems;
import java.nio.file.Files;
import java.nio.file.Path;

/**
 * Crude zeromq client that sends a file to a server
 *
 * <pre>client <address> <filename></pre>
 *
 */
public class ExampleClient {
    public static void main(String[] args)
            throws IOException
    {
        if (args.length != 2) {
            System.err.println("Usage: client <address> <filename>");
            System.exit(1);
        }
        final String address = args[0];
        final String filename = args[1];

        final Path path = FileSystems.getDefault().getPath(filename);
        final byte [] data = Files.readAllBytes(path);

        System.err.println("Sending contents of " + filename + " to " + address);
        final ZMQ.Context context = ZMQ.context(1);
        final ZMQ.Socket requester = context.socket(ZMQ.REQ);
        requester.connect(address);
        requester.send(data, 0);
        byte[] reply = requester.recv(0);
        System.out.println(new String(reply));
        requester.close();
        context.term();
    }
}
