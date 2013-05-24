package Elixys.JSON.Configuration
{
	import Elixys.JSON.JSONObject;
	
	import flash.geom.Point;
	import flash.utils.flash_proxy;
	
	public class Configuration extends JSONObject
	{
		// Constructor
		public function Configuration(data:String, existingcontent:Object = null)
		{
			// Call the base constructor
			super(data, existingcontent);
			
			// Validate the object type
			if ((Type != null) && (Type != TYPE))
			{
				throw new Error("Object type mismatch");
			}
		}
		
		// Static type
		public static function get TYPE():String
		{
			return "configuration";
		}
		
		// Data wrappers
		public function get Name():String
		{
			return super.flash_proxy::getProperty("name");
		}
		public function get Version():String
		{
			return super.flash_proxy::getProperty("version");
		}
		public function get Debug():Boolean
		{
			var sDebug:String = super.flash_proxy::getProperty("version");
			return (sDebug == "true");
		}
		public function get SupportedOperations():Array
		{
			return super.flash_proxy::getProperty("supportedoperations");
		}
		public function get Reactors():uint
		{
			return super.flash_proxy::getProperty("reactors");
		}
		public function get ReagentsPerReactor():uint
		{
			return super.flash_proxy::getProperty("reagentsperreactor");
		}
		public function get DeliveryPositionsPerReactor():uint
		{
			return super.flash_proxy::getProperty("deliverypositionsperreactor");
		}
		public function get ElutePositionsPerReactor():uint
		{
			return super.flash_proxy::getProperty("elutepositionsperreactor");
		}
		public function get ReactorLayoutDimensions():Point
		{
			// Parse the reactor layout dimensions
			if (m_pReactorLayoutDimensions == null)
			{
				m_pReactorLayoutDimensions = ParsePoint(super.flash_proxy::getProperty("reactorlayoutdimensions"));
			}
			return m_pReactorLayoutDimensions;
		}
		public function get ReactorReagentPositions():Array
		{
			// Parse the reactor reagent positions
			if (m_pReactorReagentPositions == null)
			{
				m_pReactorReagentPositions = new Array();
				var pReactorReagentPositions:Array = super.flash_proxy::getProperty("reactorreagentpositions");
				for each (var pReactorReagentPositionObject:Object in pReactorReagentPositions)
				{
					m_pReactorReagentPositions.push(ParsePoint(pReactorReagentPositionObject));
				}
			}
			return m_pReactorReagentPositions;
		}
		public function get ReactorDeliveryPositions():Array
		{
			// Parse the reactor delivery positions
			if (m_pReactorDeliveryPositions == null)
			{
				m_pReactorDeliveryPositions = new Array();
				var pReactorDeliveryPositions:Array = super.flash_proxy::getProperty("reactordeliverypositions");
				for each (var pReactorDeliveryPositionObject:Object in pReactorDeliveryPositions)
				{
					m_pReactorDeliveryPositions.push(ParsePoint(pReactorDeliveryPositionObject));
				}
			}
			return m_pReactorDeliveryPositions;
		}
		public function get ReactorElutePositions():Array
		{
			// Parse the reactor elute positions
			if (m_pReactorElutePositions == null)
			{
				m_pReactorElutePositions = new Array();
				var pReactorElutePositions:Array = super.flash_proxy::getProperty("reactorelutepositions");
				for each (var pReactorElutePositionObject:Object in pReactorElutePositions)
				{
					m_pReactorElutePositions.push(ParsePoint(pReactorElutePositionObject));
				}
			}
			return m_pReactorElutePositions;
		}
		public function ParsePoint(pPointObject:Object):Point
		{
			return new Point(pPointObject.x, pPointObject.y);
		}
		
		// State components
		protected var m_pReactorLayoutDimensions:Point;
		protected var m_pReactorReagentPositions:Array;
		protected var m_pReactorDeliveryPositions:Array;
		protected var m_pReactorElutePositions:Array;
	}
}