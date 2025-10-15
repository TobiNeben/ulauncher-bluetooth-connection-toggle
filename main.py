import json
import logging
import os
from ulauncher.api.client.Extension import Extension
from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.shared.event import KeywordQueryEvent, ItemEnterEvent
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.action.ExtensionCustomAction import ExtensionCustomAction
from ulauncher.api.shared.action.HideWindowAction import HideWindowAction

logger = logging.getLogger(__name__)


class BluetoothTM(Extension):

    def __init__(self):
        super(BluetoothTM, self).__init__()
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())
        self.subscribe(ItemEnterEvent, ItemEnterEventListener())


class KeywordQueryEventListener(EventListener):

    def on_event(self, event, extension):
        items = []
        unconnected_devices = []
        connected_devices = []
        logger.info('preferences %s' % json.dumps(extension.preferences))

        # get  paired bluetooth devices
        ret = os.popen("bash -c 'bluetoothctl paired-devices'").read()
        for line in ret.splitlines():
            parts = line.split()
            if len(parts) < 3:
                continue
            device_name = ' '.join(parts[2:])
            device_address = parts[1]
            connected = False
            # check if device is connected
            info = os.popen(f"bash -c 'bluetoothctl info {device_address}'").read()
            if 'Connected: yes' in info:
                connected = True

           
            if connected:
                connected_devices.append(ExtensionResultItem(
                    icon='images/disconnect.png',
                    name=device_name,
                    description=device_address,
                    on_enter=ExtensionCustomAction('disconnect ' + device_address, keep_app_open=True)))
            else:
                unconnected_devices.append(ExtensionResultItem(
                    icon='images/connect.png',
                    name=device_name,
                    description=device_address,
                    on_enter=ExtensionCustomAction('connect ' + device_address, keep_app_open=True)))
        items.extend(unconnected_devices)
        items.extend(connected_devices)

        return RenderResultListAction(items)


class ItemEnterEventListener(EventListener):

    def on_event(self, event, extension):
        data = event.get_data()
        if (data == 'none'):
            return HideWindowAction()

        ret = os.system(
            f"bash -c 'timeout 8s bluetoothctl {data}'")

        if ret == 0:
            prompt = data.split()[0] + "ed Successfully"
        else:
            prompt = data.split()[0] + "ion Failed"

        return RenderResultListAction([ExtensionResultItem(icon='images/icon.png',
                                                           name=prompt,
                                                           on_enter=HideWindowAction())])


if __name__ == '__main__':
    BluetoothTM().run()
