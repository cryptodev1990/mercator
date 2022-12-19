-- Adapted from generic.lua and unitable.lua scripts

-- Set this to the projection you want to use
-- local srid = 3857
-- GEOJSON SRID
local srid = 4326

local dtable = osm2pgsql.define_table{
    name = 'osm',
    -- This will generate a column "osm_id INT8" for the id, and a column
    -- "osm_type CHAR(1)" for the type of object: N(ode), W(way), R(relation)
    ids = { type = 'any', id_column = 'osm_id', type_column = 'osm_type' },
    columns = {
        { column = 'tags',  type = 'jsonb' },
        { column = 'geom',  type = 'geometry', projection = srid, not_null = true}
        -- values: points, lines, polygons, boundary, or route
        -- these are the separate tables in generic.lua
        { column = 'category', type = 'text'}
    }
}


-- These tag keys are generally regarded as useless for most rendering. Most
-- of them are from imports or intended as internal information for mappers.
--
-- If a key ends in '*' it will match all keys with the specified prefix.
--
-- If you want some of these keys, perhaps for a debugging layer, just
-- delete the corresponding lines.
local delete_keys = {
    -- "mapper" keys
    'attribution',
    'comment',
    'created_by',
    'fixme',
    'note',
    'note:*',
    'odbl',
    'odbl:note',
    'source',
    'source:*',
    'source_ref',

    -- "import" keys

    -- Corine Land Cover (CLC) (Europe)
    'CLC:*',

    -- Geobase (CA)
    'geobase:*',
    -- CanVec (CA)
    'canvec:*',

    -- osak (DK)
    'osak:*',
    -- kms (DK)
    'kms:*',

    -- ngbe (ES)
    -- See also note:es and source:file above
    'ngbe:*',

    -- Friuli Venezia Giulia (IT)
    'it:fvg:*',

    -- KSJ2 (JA)
    -- See also note:ja and source_ref above
    'KSJ2:*',
    -- Yahoo/ALPS (JA)
    'yh:*',

    -- LINZ (NZ)
    'LINZ2OSM:*',
    'linz2osm:*',
    'LINZ:*',
    'ref:linz:*',

    -- WroclawGIS (PL)
    'WroclawGIS:*',
    -- Naptan (UK)
    'naptan:*',

    -- TIGER (US)
    'tiger:*',
    -- GNIS (US)
    'gnis:*',
    -- National Hydrography Dataset (US)
    'NHD:*',
    'nhd:*',
    -- mvdgis (Montevideo, UY)
    'mvdgis:*',

    -- EUROSHA (Various countries)
    'project:eurosha_2012',

    -- UrbIS (Brussels, BE)
    'ref:UrbIS',

    -- NHN (CA)
    'accuracy:meters',
    'sub_sea:type',
    'waterway:type',
    -- StatsCan (CA)
    'statscan:rbuid',

    -- RUIAN (CZ)
    'ref:ruian:addr',
    'ref:ruian',
    'building:ruian:type',
    -- DIBAVOD (CZ)
    'dibavod:id',
    -- UIR-ADR (CZ)
    'uir_adr:ADRESA_KOD',

    -- GST (DK)
    'gst:feat_id',

    -- Maa-amet (EE)
    'maaamet:ETAK',
    -- FANTOIR (FR)
    'ref:FR:FANTOIR',

    -- 3dshapes (NL)
    '3dshapes:ggmodelk',
    -- AND (NL)
    'AND_nosr_r',

    -- OPPDATERIN (NO)
    'OPPDATERIN',
    -- Various imports (PL)
    'addr:city:simc',
    'addr:street:sym_ul',
    'building:usage:pl',
    'building:use:pl',
    -- TERYT (PL)
    'teryt:simc',

    -- RABA (SK)
    'raba:id',
    -- DCGIS (Washington DC, US)
    'dcgis:gis_id',
    -- Building Identification Number (New York, US)
    'nycdoitt:bin',
    -- Chicago Building Inport (US)
    'chicago:building_id',
    -- Louisville, Kentucky/Building Outlines Import (US)
    'lojic:bgnum',
    -- MassGIS (Massachusetts, US)
    'massgis:way_id',
    -- Los Angeles County building ID (US)
    'lacounty:*',
    -- Address import from Bundesamt für Eich- und Vermessungswesen (AT)
    'at_bev:addr_date',

    -- misc
    'import',
    'import_uuid',
    'OBJTYPE',
    'SK53_bulk:load',
    'mml:class'
}

-- The osm2pgsql.make_clean_tags_func() function takes the list of keys
-- and key prefixes defined above and returns a function that can be used
-- to clean those tags out of a Lua table. The clean_tags function will
-- return true if it removed all tags from the table.
local clean_tags = osm2pgsql.make_clean_tags_func(delete_keys)

-- Helper function that looks at the tags and decides if this is possibly
-- an area.

area_tags = {}
area_tags["addr:*"] = {}
area_tags["advertising"] = {['billboard'] = true}
area_tags["aerialway"] = {['cable_car'] = true, ['chair_lift'] = true, ['drag_lift'] = true, ['gondola'] = true, ['goods'] = true, ['j-bar'] = true, ['magic_carpet'] = true, ['mixed_lift'] = true, ['platter'] = true, ['rope_tow'] = true, ['t-bar'] = true, ['zip_line'] = true}
area_tags["aeroway"] = {['jet_bridge'] = true, ['parking_position'] = true, ['runway'] = true, ['taxiway'] = true}
area_tags["allotments"] = {}
area_tags["amenity"] = {['bench'] = true, ['weighbridge'] = true}
area_tags["area:highway"] = {}
area_tags["attraction"] = {['dark_ride'] = true, ['river_rafting'] = true, ['summer_toboggan'] = true, ['train'] = true, ['water_slide'] = true}
area_tags["bridge:support"] = {}
area_tags["building"] = {}
area_tags["building:part"] = {}
area_tags["cemetery"] = {}
area_tags["club"] = {}
area_tags["craft"] = {}
area_tags["demolished:building"] = {}
area_tags["disused:amenity"] = {}
area_tags["disused:railway"] = {}
area_tags["disused:shop"] = {}
area_tags["emergency"] = {['designated'] = true, ['destination'] = true, ['no'] = true, ['official'] = true, ['private'] = true, ['yes'] = true}
area_tags["golf"] = {['cartpath'] = true, ['hole'] = true, ['path'] = true}
area_tags["healthcare"] = {}
area_tags["historic"] = {}
area_tags["indoor"] = {['corridor'] = true, ['wall'] = true}
area_tags["industrial"] = {}
area_tags["internet_access"] = {}
area_tags["junction"] = {}
area_tags["landuse"] = {}
area_tags["leisure"] = {['slipway'] = true, ['track'] = true}
area_tags["man_made"] = {['yes'] = true, ['breakwater'] = true, ['carpet_hanger'] = true, ['crane'] = true, ['cutline'] = true, ['dyke'] = true, ['embankment'] = true, ['goods_conveyor'] = true, ['groyne'] = true, ['pier'] = true, ['pipeline'] = true, ['torii'] = true, ['video_wall'] = true}
area_tags["military"] = {['trench'] = true}
area_tags["natural"] = {['bay'] = true, ['cliff'] = true, ['coastline'] = true, ['ridge'] = true, ['strait'] = true, ['tree_row'] = true, ['valley'] = true}
area_tags["office"] = {}
area_tags["piste:type"] = {['downhill'] = true, ['hike'] = true, ['ice_skate'] = true, ['nordic'] = true, ['skitour'] = true, ['sled'] = true, ['sleigh'] = true}
area_tags["place"] = {}
area_tags["playground"] = {['activitypanel'] = true, ['balancebeam'] = true, ['basketswing'] = true, ['bridge'] = true, ['climbingwall'] = true, ['hopscotch'] = true, ['horizontal_bar'] = true, ['seesaw'] = true, ['slide'] = true, ['structure'] = true, ['swing'] = true, ['tunnel_tube'] = true, ['water'] = true, ['zipwire'] = true}
area_tags["police"] = {}
area_tags["polling_station"] = {}
area_tags["power"] = {['cable'] = true, ['line'] = true, ['minor_line'] = true}
area_tags["public_transport"] = {['platform'] = true}
area_tags["residential"] = {}
area_tags["seamark:type"] = {}
area_tags["shop"] = {}
area_tags["telecom"] = {}
area_tags["tourism"] = {['artwork'] = true, ['attraction'] = true}
area_tags["traffic_calming"] = {['yes'] = true, ['bump'] = true, ['chicane'] = true, ['choker'] = true, ['cushion'] = true, ['dip'] = true, ['hump'] = true, ['island'] = true, ['mini_bumps'] = true, ['rumble_strip'] = true}
area_tags["waterway"] = {['canal'] = true, ['dam'] = true, ['ditch'] = true, ['drain'] = true, ['fish_pass'] = true, ['lock_gate'] = true, ['river'] = true, ['stream'] = true, ['tidal_channel'] = true, ['weir'] = true}


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
    return false
end

function osm2pgsql.process_node(object)
    if clean_tags(object.tags) then
        return
    end

    dtable:insert({
        tags = object.tags,
        geom = object:as_point(),
    })

end

function osm2pgsql.process_way(object)
    if clean_tags(object.tags) then
        return
    end

    if object.is_closed and has_area_tags(object.tags) then
        -- polygon
        dtable:insert({
            tags = object.tags,
            geom = object:as_polygon(),
        })
        return
    end

    dtable:insert({
        tags = object.tags,
        geom = object:as_linestring():line_merge(),
    })

end

function osm2pgsql.process_relation(object)
    -- keep the type tag
    -- local relation_type = object:grab_tag('type')
    local relation_type = object.tags.type

    if clean_tags(object.tags) then
        return
    end

    -- boundary
    if relation_type == 'boundary' or relation_type == 'multipolygon' then
        dtable:insert({
            tags = object.tags,
            geom = object:as_multipolygon(),
        })
        return
    end

    dtable:insert({
        tags = object.tags,
        geom = object:as_multilinestring():line_merge(),
    })

end
