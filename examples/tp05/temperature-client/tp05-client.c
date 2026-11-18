
#include "contiki.h"
#include "net/routing/routing.h"
#include "net/ipv6/uiplib.h"
#include "sys/node-id.h"
#include "coap-engine.h"
#include "coap-blocking-api.h"

#include <stdio.h>
#include <string.h>
#include <stdint.h>

#define SEND_INTERVAL (30 * CLOCK_SECOND)

static struct etimer timer;
static coap_endpoint_t server_ep;
static coap_message_t request[1];

static char payload[64];
static uint32_t sequence = 0;

/* Discover the RPL Root IPv6 address */
static int
find_server(void)
{
  uip_ipaddr_t root_ip;
  char ip[UIPLIB_IPV6_MAX_STR_LEN];
  char uri[80];

  if(!NETSTACK_ROUTING.node_is_reachable() ||
     !NETSTACK_ROUTING.get_root_ipaddr(&root_ip)) {
    return 0;
  }

  uiplib_ipaddr_snprint(ip, sizeof(ip), &root_ip);
  snprintf(uri, sizeof(uri), "coap://[%s]", ip);

  return coap_endpoint_parse(uri, strlen(uri),
                             &server_ep);
}

/* Response callback */
static void
response_handler(coap_message_t *response)
{
  if(response == NULL) {
    printf("TEMP_TIMEOUT id=%u seq=%lu\n",
           node_id, (unsigned long)sequence);
    return;
  }

  if(response->code == CHANGED_2_04) {
    printf("TEMP_ACK id=%u seq=%lu\n",
           node_id, (unsigned long)sequence);
  } else {
    printf("TEMP_ERROR code=%u\n", response->code);
  }
}

PROCESS(temperature_client, "Temperature Sensor");
AUTOSTART_PROCESSES(&temperature_client);

PROCESS_THREAD(temperature_client, ev, data)
{
  static int temp_x10;

  PROCESS_BEGIN();

  /* Stagger the first transmissions */
  etimer_set(&timer, (10 + node_id * 2) * CLOCK_SECOND);

  while(1) {

    PROCESS_WAIT_EVENT_UNTIL(etimer_expired(&timer));

    if(!find_server()) {
      printf("Waiting for RPL Root...\n");
      etimer_reset(&timer);
      continue;
    }

    /* Simulated temperature in tenths of a degree */
    temp_x10 = 215 + node_id * 3 + (sequence % 7);

    snprintf(payload, sizeof(payload),
             "id=%u,seq=%lu,temp=%d.%d",
             node_id, (unsigned long)sequence,
             temp_x10 / 10, temp_x10 % 10);

    printf("TEMP_TX %s\n", payload);

    coap_init_message(request, COAP_TYPE_CON,
                      COAP_POST, 0);

    coap_set_header_uri_path(request,
                             "sensors/temperature");

    coap_set_header_content_format(request, TEXT_PLAIN);

    coap_set_payload(request, payload, strlen(payload));

    COAP_BLOCKING_REQUEST(&server_ep, request,
                          response_handler);

    sequence++;
    etimer_set(&timer, SEND_INTERVAL);
  }

  PROCESS_END();
}
