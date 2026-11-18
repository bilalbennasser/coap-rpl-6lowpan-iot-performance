
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
static uint8_t non_packet[COAP_MAX_PACKET_SIZE];

static char payload[64];
static uint32_t sequence = 0;
static uint32_t request_seq;
static clock_time_t request_start;


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


PROCESS(temperature_client, "Temperature Sensor");
AUTOSTART_PROCESSES(&temperature_client);

PROCESS_THREAD(temperature_client, ev, data)
{
  static int temp_x10;

  PROCESS_BEGIN();

  /* Stagger the first transmissions */
  etimer_set(&timer, (5 * 60 + 10 + node_id * 2) * CLOCK_SECOND);

  while(1) {

    PROCESS_WAIT_EVENT_UNTIL(etimer_expired(&timer));
    if(clock_seconds() >= 35 * 60) {
      printf("TP07_END id=%u\n", node_id);
      break;
    }


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

    coap_init_message(request, COAP_TYPE_NON,
                      COAP_POST, 0);

    coap_set_header_uri_path(request,
                             "sensors/temperature");

    coap_set_header_content_format(request, TEXT_PLAIN);

    coap_set_payload(request, payload, strlen(payload));


    request_seq = sequence;
    request_start = clock_time();

    
    request->mid = coap_get_mid();

    size_t packet_len =
      coap_serialize_message(request, non_packet);

    if(packet_len == 0 ||
       packet_len > sizeof(non_packet)) {
      printf("TP08_NON_ERROR id=%u seq=%lu\n",
             node_id, (unsigned long)sequence);
    } else {
      int sent = coap_sendto(
          &server_ep, non_packet, (uint16_t)packet_len);

      if(sent < 0) {
        printf("TP08_NON_ERROR id=%u seq=%lu\n",
               node_id, (unsigned long)sequence);
      } else {
        printf("TP08_NON_SEND id=%u seq=%lu\n",
               node_id, (unsigned long)sequence);
      }
    }


    sequence++;
    etimer_set(&timer, SEND_INTERVAL);
  }

  PROCESS_END();
}
