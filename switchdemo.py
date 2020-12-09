from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet
from ryu.lib.packet import ethernet
from ryu.app import simple_switch_13
from ryu.lib import hub
from operator import attrgetter
 
 
class ExampleSwitch13(simple_switch_13.SimpleSwitch13):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]
 
    def __init__(self, *args, **kwargs):
        super(ExampleSwitch13, self).__init__(*args, **kwargs)
        # initialize mac address table.
        self.mac_to_port = {}
        #######new function#######
        self.datapaths = {}
        self.monitor_thread = hub.spawn(self.monitor)


    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
 
        # install the table-miss flow entry.
        match = parser.OFPMatch()
        actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER,
                                          ofproto.OFPCML_NO_BUFFER)]
        self.add_flow(datapath, 0, match, actions)

    def add_flow(self, datapath, priority, match, actions):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
 
        # construct flow_mod message and send it.
        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS,
                                             actions)]
        mod = parser.OFPFlowMod(datapath=datapath, priority=priority,
                                match=match, instructions=inst)
        datapath.send_msg(mod)
 
    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def _packet_in_handler(self, ev):
        msg = ev.msg
        datapath = msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
 
        # get Datapath ID to identify OpenFlow switches.
        dpid = datapath.id
        self.mac_to_port.setdefault(dpid, {})
 
        # analyse the received packets using the packet library.
        pkt = packet.Packet(msg.data)
        eth_pkt = pkt.get_protocol(ethernet.ethernet)
        dst = eth_pkt.dst
        src = eth_pkt.src
 
        # get the received port number from packet_in message.
        in_port = msg.match['in_port']
 
        self.logger.info("packet in %s %s %s %s", dpid, src, dst, in_port)
 
        # learn a mac address to avoid FLOOD next time.
        self.mac_to_port[dpid][src] = in_port
 
        # if the destination mac address is already learned,
        # decide which port to output the packet, otherwise FLOOD.
        if dst in self.mac_to_port[dpid]:
            out_port = self.mac_to_port[dpid][dst]
        else:
            out_port = ofproto.OFPP_FLOOD
 
        # construct action list.
        actions = [parser.OFPActionOutput(out_port)]
 
        # install a flow to avoid packet_in next time.
        if out_port != ofproto.OFPP_FLOOD:
            match = parser.OFPMatch(in_port=in_port, eth_dst=dst)
            self.add_flow(datapath, 1, match, actions)
 
        # construct packet_out message and send it.
        out = parser.OFPPacketOut(datapath=datapath,
                                  buffer_id=ofproto.OFP_NO_BUFFER,
                                  in_port=in_port, actions=actions,
                                  data=msg.data)
        datapath.send_msg(out)

    ############################
    #######new function#########
    ############################
    @set_ev_cls(ofp_event.EventOFPStateChange, [MAIN_DISPATCHER])
    def state_change_handler(self, ev):
        datapath = ev.datapath
        if ev.state == MAIN_DISPATCHER:
            if datapath.id not in self.datapaths:
                print('register datapath: ', datapath.id)
            self.datapaths[datapath.id] = datapath


    def monitor(self):
        while True:
            for dp in self.datapaths.values():
                print('collect data ')
                self.request_stats(dp)
            hub.sleep(10)

    def request_stats(self, datapath):
        self.logger.debug('send stats request: %016x', datapath.id)
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        # To collect dp_id, pkt_count, byte_count
        req = parser.OFPFlowStatsRequest(datapath)
        datapath.send_msg(req)

        # To collect dp_id, port_no, rx_bytes, rx_pkts, tx_bytes, tx_pkts
        req = parser.OFPPortStatsRequest(datapath, 0, ofproto.OFPP_ANY)
        datapath.send_msg(req)

    @set_ev_cls(ofp_event.EventOFPFlowStatsReply, MAIN_DISPATCHER)
    def _flow_stats_reply_handler(self, ev):
        body = ev.msg.body
        #self.logger.info('datapath         in-port  eth-dst           out-port packets  bytes')
        #self.logger.info('---------------- -------- ----------------- -------- -------- --------')
        for stat in sorted([flow for flow in body if (flow.priority == 1)], key=lambda flow:
        (flow.match['in_port'], flow.match['eth_dst'])):
            print("\n" + str(ev.msg.datapath.id) + "," + str(stat.match['in_port']) + "," +
                       str(stat.match['eth_dst']) + "," + str(stat.packet_count) + "," + str(stat.byte_count))
            with open("flowdata.txt", "a") as myfile:
                myfile.write("\n"  + str(stat.match['in_port']) + "," +
                        + str(stat.packet_count) + "," + str(stat.byte_count)+","+str(stat.duration_sec)+","+str(stat.idle_timeout)+"," +str(stat.hard_timeout))

    @set_ev_cls(ofp_event.EventOFPPortStatsReply, MAIN_DISPATCHER)
    def _port_stats_reply_handler(self, ev):
        body = ev.msg.body
        #self.logger.info('datapath         port     rx-pkts  rx-bytes rx-error tx-pkts  tx-bytes tx-error')
        #self.logger.info('---------------- -------- -------- -------- -------- -------- -------- --------')
        for stat in sorted(body, key=attrgetter('port_no')):
            if stat.port_no <= 10:

                #self.logger.info('%016x %8x %8d %8d %8d %8d %8d %8d',ev.msg.datapath.id, stat.port_no,stat.rx_packets, stat.rx_bytes, stat.rx_errors,stat.tx_packets, stat.tx_bytes, stat.tx_errors)

                print("\n{},{},{},{},{},{}".format(ev.msg.datapath.id, stat.port_no, stat.rx_bytes,
                                                        stat.rx_packets, stat.tx_bytes, stat.tx_packets))
                with open("Portdata.txt", "a") as myfile:
                    myfile.write("\n{},{},{},{},{},{}".format(stat.port_no, stat.rx_bytes,
                                                        stat.rx_packets, stat.tx_bytes, stat.tx_packets,stat.duration_sec))
