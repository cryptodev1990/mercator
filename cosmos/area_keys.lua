
areakeys = {}
areakeys["addr:*"] = {}
areakeys["advertising"] = {['billboard'] = true}
areakeys["aerialway"] = {['cable_car'] = true, ['chair_lift'] = true, ['drag_lift'] = true, ['gondola'] = true, ['goods'] = true, ['j-bar'] = true, ['magic_carpet'] = true, ['mixed_lift'] = true, ['platter'] = true, ['rope_tow'] = true, ['t-bar'] = true, ['zip_line'] = true}
areakeys["aeroway"] = {['jet_bridge'] = true, ['parking_position'] = true, ['runway'] = true, ['taxiway'] = true}
areakeys["allotments"] = {}
areakeys["amenity"] = {['bench'] = true, ['weighbridge'] = true}
areakeys["area:highway"] = {}
areakeys["attraction"] = {['dark_ride'] = true, ['river_rafting'] = true, ['summer_toboggan'] = true, ['train'] = true, ['water_slide'] = true}
areakeys["bridge:support"] = {}
areakeys["building"] = {}
areakeys["building:part"] = {}
areakeys["cemetery"] = {}
areakeys["club"] = {}
areakeys["craft"] = {}
areakeys["demolished:building"] = {}
areakeys["disused:amenity"] = {}
areakeys["disused:railway"] = {}
areakeys["disused:shop"] = {}
areakeys["emergency"] = {['designated'] = true, ['destination'] = true, ['no'] = true, ['official'] = true, ['private'] = true, ['yes'] = true}
areakeys["golf"] = {['cartpath'] = true, ['hole'] = true, ['path'] = true}
areakeys["healthcare"] = {}
areakeys["historic"] = {}
areakeys["indoor"] = {['corridor'] = true, ['wall'] = true}
areakeys["industrial"] = {}
areakeys["internet_access"] = {}
areakeys["junction"] = {}
areakeys["landuse"] = {}
areakeys["leisure"] = {['slipway'] = true, ['track'] = true}
areakeys["man_made"] = {['yes'] = true, ['breakwater'] = true, ['carpet_hanger'] = true, ['crane'] = true, ['cutline'] = true, ['dyke'] = true, ['embankment'] = true, ['goods_conveyor'] = true, ['groyne'] = true, ['pier'] = true, ['pipeline'] = true, ['torii'] = true, ['video_wall'] = true}
areakeys["military"] = {['trench'] = true}
areakeys["natural"] = {['bay'] = true, ['cliff'] = true, ['coastline'] = true, ['ridge'] = true, ['strait'] = true, ['tree_row'] = true, ['valley'] = true}
areakeys["office"] = {}
areakeys["piste:type"] = {['downhill'] = true, ['hike'] = true, ['ice_skate'] = true, ['nordic'] = true, ['skitour'] = true, ['sled'] = true, ['sleigh'] = true}
areakeys["place"] = {}
areakeys["playground"] = {['activitypanel'] = true, ['balancebeam'] = true, ['basketswing'] = true, ['bridge'] = true, ['climbingwall'] = true, ['hopscotch'] = true, ['horizontal_bar'] = true, ['seesaw'] = true, ['slide'] = true, ['structure'] = true, ['swing'] = true, ['tunnel_tube'] = true, ['water'] = true, ['zipwire'] = true}
areakeys["police"] = {}
areakeys["polling_station"] = {}
areakeys["power"] = {['cable'] = true, ['line'] = true, ['minor_line'] = true}
areakeys["public_transport"] = {['platform'] = true}
areakeys["residential"] = {}
areakeys["seamark:type"] = {}
areakeys["shop"] = {}
areakeys["telecom"] = {}
areakeys["tourism"] = {['artwork'] = true, ['attraction'] = true}
areakeys["traffic_calming"] = {['yes'] = true, ['bump'] = true, ['chicane'] = true, ['choker'] = true, ['cushion'] = true, ['dip'] = true, ['hump'] = true, ['island'] = true, ['mini_bumps'] = true, ['rumble_strip'] = true}
areakeys["waterway"] = {['canal'] = true, ['dam'] = true, ['ditch'] = true, ['drain'] = true, ['fish_pass'] = true, ['lock_gate'] = true, ['river'] = true, ['stream'] = true, ['tidal_channel'] = true, ['weir'] = true}

function has_area_tags(tags)
    if tags.area == 'yes' then
        return true
    end
    if tags.area == 'no' then
        return false
    end
    for key, value in pairs(tags) do
        if area_tags[key] and not area_tags[key][value] then
            return true
        end
        if string.find(key, 'addr:*') then
            return true
        end
    end
end