# New Introduction to mu {olx-org=testing_org olx-course=all-about-mu olx-url_name=session1}

## Chapter 1

### Sequential 1_1

#### Course Syllabus

::: {mu-type=video}

##### Video

![](https://s3.amazonaws.com/edx-course-videos/edx-edx101/EDXSPCPJSP13-H010000_100.mp4)

:::

##### Some html content

Each one of these paragraphs should result in a different `<p>` tag.

We can even include images here:

![](https://www.google.com/images/logo.png)

```c
printf("Hello world!\n");
```

Raw code:

    import base64
    base64.decodebytes(b'UmFjbGV0dGUgY2hlZXNlIGlzIHRoZSBiZXN0')

#### Problems

::: {mu-type=mcq}

#### Multiple choice question

What is the answer to Life, the Universe, and Everything?

* ✅ 6 x 7
* ❌ 666
* ❌ 0
* ✅ 42

:::

::: {mu-type=ftq}

#### Free text question

How many legs does a healthy snake have?

<!-- All accepted answers are listed below -->

* None
* Zero
* 0

:::

### Second sequential

#### Test unit

This is a test with some code

```c
#include "esp_wifi.h"
#include "string.h"
#include "esp_log.h"


static const char* TAG = "main"; // Used for logging
// ...

void wifi_init_softap()
{
    esp_netif_init();
    esp_event_loop_create_default();
    esp_netif_create_default_wifi_ap();

    wifi_init_config_t cfg = WIFI_INIT_CONFIG_DEFAULT(); // always start with this

    esp_wifi_init(&cfg);

    esp_event_handler_instance_register(WIFI_EVENT,
                                                        ESP_EVENT_ANY_ID,
                                                        &wifi_event_handler,
                                                        NULL,
                                                        NULL);

    wifi_config_t wifi_config = {
        .ap = {
            .ssid = ESP_WIFI_SSID,
            .ssid_len = strlen(ESP_WIFI_SSID),
            .channel = ESP_WIFI_CHANNEL,
            .password = ESP_WIFI_PASS,
            .max_connection = MAX_STA_CONN,
            .authmode = WIFI_AUTH_WPA2_PSK,
            .pmf_cfg = {
                .required = true,
            },
        },
    };


    esp_wifi_set_mode(WIFI_MODE_AP);
    esp_wifi_set_config(WIFI_IF_AP, &wifi_config);
    esp_wifi_start();

    ESP_LOGI(TAG, "wifi_init_softap finished. SSID:%s password:%s channel:%d",
             ESP_WIFI_SSID, ESP_WIFI_PASS, ESP_WIFI_CHANNEL);
}
```

## Second chapter

### Sequential 2.1

#### Course Syllabus 2

::: {mu-type=video}

##### Video

![](https://s3.amazonaws.com/edx-course-videos/edx-edx101/EDXSPCPJSP13-H010000_100.mp4)

:::

##### Some html content

Each one of these paragraphs should result in a different `<p>` tag.

We can even include images here:

![](https://www.google.com/images/logo.png)

```c
printf("Hello world!\n");
```

Raw code:

    import base64
    base64.decodebytes(b'UmFjbGV0dGUgY2hlZXNlIGlzIHRoZSBiZXN0')

#### Problems 2

::: {mu-type=mcq}

#### Multiple choice question

What is the answer to Life, the Universe, and Everything?

* ✅ 6 x 7
* ❌ 666
* ❌ 0
* ✅ 42

:::

::: {mu-type=ftq}

#### Free text question

How many legs does a healthy snake have?

<!-- All accepted answers are listed below -->

* None
* Zero
* 0

:::
