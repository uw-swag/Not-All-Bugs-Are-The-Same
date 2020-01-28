import java.io.IOException;
import org.apache.http.HttpEntity;
import org.apache.http.client.ClientProtocolException;
import org.apache.http.client.methods.CloseableHttpResponse;
import org.apache.http.client.methods.HttpGet;
import org.apache.http.impl.client.CloseableHttpClient;
import org.apache.http.impl.client.HttpClients;
import org.apache.http.util.EntityUtils;

import java.io.FileWriter;
import java.io.IOException;

import java.util.Iterator;

import org.json.JSONArray;
import org.json.JSONObject;

public class Main {
    public static void main(String[] args) throws ClientProtocolException, IOException {


        //HttpGet httpGet = new HttpGet("http://localhost:9000/api/measures/component?component=test&metricKeys=complexity");
        HttpGet httpGetComponents = new HttpGet("http://localhost:9000/api/components/search?qualifiers=FIL");


        //Get JSON for all components (file level)
        JSONArray componentsArray;
        try(CloseableHttpClient httpClient = HttpClients.createDefault();
            CloseableHttpResponse componentResponse = httpClient.execute(httpGetComponents);) {
            HttpEntity componentEntity = componentResponse.getEntity();
            String componentString = EntityUtils.toString(componentEntity );
            JSONObject components = new JSONObject(componentString);
            componentsArray = (JSONArray) components.get("components");
        }


        JSONArray cyclomaticComplexity = new JSONArray();


        //Iterate through component keys of each file
        for (int i=0; i < componentsArray.length(); i++){
            String fileKey = componentsArray.getJSONObject(i).get("key").toString();

            //Get cyclomatic complexity for each file
            HttpGet httpGetMeasure = new HttpGet("http://localhost:9000/api/measures/component?component="+fileKey+"&metricKeys=complexity");
            try(CloseableHttpClient httpClient = HttpClients.createDefault();
                CloseableHttpResponse metricResponse = httpClient.execute(httpGetMeasure);) {
                HttpEntity metricEntity = metricResponse.getEntity();
                String metricString = EntityUtils.toString(metricEntity );
                JSONObject metricObject = new JSONObject(metricString);

                //Get file path and CC
                String path = metricObject.getJSONObject("component").get("path").toString();
                String cc = "0";

                //Measures are in an array, so have to iterate though JSONArray to find CC
                JSONArray measuresArray = metricObject.getJSONObject("component").getJSONArray("measures");
                for (int j=0; j < measuresArray.length(); j++) {
                    String metric = measuresArray.getJSONObject(j).get("metric").toString();
                    if (metric.equals("complexity")){
                        cc = measuresArray.getJSONObject(j).get("value").toString();
                    }
                }

                //Add desired metrics to new JSONArray
                JSONObject fileMeasures = new JSONObject();
                fileMeasures.put("path",path);
                fileMeasures.put("CC",cc);

                JSONObject fileObject = new JSONObject();
                fileObject.put("file",fileMeasures);

                cyclomaticComplexity.put(fileObject);

            }

        }


        //Write JSON file
        try (FileWriter file = new FileWriter("metrics.json")) {

            file.write(cyclomaticComplexity.toString());
            file.flush();

        } catch (IOException e) {
            e.printStackTrace();
        }



    }
}