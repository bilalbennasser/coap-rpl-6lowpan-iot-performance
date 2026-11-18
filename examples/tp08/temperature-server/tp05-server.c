
#include "contiki.h"
#include "net/routing/routing.h"
#include "coap-engine.h"

#include <stdio.h>
#include <string.h>

/* CoAP POST handler */
static void
temperature_post(coap_message_t *request,
                 coap_message_t *response,
                 uint8_t *buffer,
                 uint16_t preferred_size,
                 int32_t *offset)
{
  const uint8_t *payload = NULL;
  int len = coap_get_payload(request, &payload);

  if(len <= 0 || len >= 64) {
    coap_set_status_code(response, BAD_REQUEST_4_00);
    return;
  }

  /* Display the received temperature */
  printf("TEMP_RX %.*s\n", len, (const char *)payload);

  /* Send an acknowledgment */
  static const char ack[] = "OK";

  coap_set_status_code(response, CHANGED_2_04);
  coap_set_header_content_format(response, TEXT_PLAIN);
  coap_set_payload(response, ack, sizeof(ack) - 1);
}

/* Register our CoAP resource */
RESOURCE(res_temperature_report,
         "title=\"Temperature report\"",
         NULL,
         temperature_post,
         NULL,
         NULL);

PROCESS(temperature_server, "Temperature CoAP Server");
AUTOSTART_PROCESSES(&temperature_server);

PROCESS_THREAD(temperature_server, ev, data)
{
  PROCESS_BEGIN();

  NETSTACK_ROUTING.root_start();

  coap_activate_resource(&res_temperature_report,
                         "sensors/temperature");

  printf("TP05 Server started - RPL Root\n");

  while(1) {
    PROCESS_WAIT_EVENT();
  }

  PROCESS_END();
}
