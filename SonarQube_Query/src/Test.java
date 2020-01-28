import java.io.IOException;
import org.apache.http.HttpEntity;
import org.apache.http.client.ClientProtocolException;
import org.apache.http.client.methods.CloseableHttpResponse;
import org.apache.http.client.methods.HttpGet;
import org.apache.http.impl.client.CloseableHttpClient;
import org.apache.http.impl.client.HttpClients;
import org.apache.http.util.EntityUtils;



public class Test {
    public static void main(String[] args) throws ClientProtocolException, IOException {

        HttpGet httpGetComponents = new HttpGet("http://localhost:9000");

        try(CloseableHttpClient httpClient = HttpClients.createDefault();
            CloseableHttpResponse componentResponse = httpClient.execute(httpGetComponents);) {
            HttpEntity componentEntity = componentResponse.getEntity();
            String componentString = EntityUtils.toString(componentEntity);

            System.out.println("Seems to work!");
        }

        catch(Exception e){
            System.out.println("Hmmm problem:\n"+e);
        }

    }
}