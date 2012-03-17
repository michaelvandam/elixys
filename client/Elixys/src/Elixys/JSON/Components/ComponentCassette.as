package Elixys.JSON.Components
{
	import Elixys.JSON.State.Reagent;
	
	import flash.utils.flash_proxy;
	
	public class ComponentCassette extends ComponentBase
	{
		// Constructor
		public function ComponentCassette(data:String = null, existingcontent:Object = null)
		{
			// Call the base constructor
			super(data, existingcontent);
			
			// Validate the object type
			if ((ComponentType != null) && (ComponentType != COMPONENTTYPE))
			{
				throw new Error("State object mismatch");
			}
		}

		// Static component type
		public static function get COMPONENTTYPE():String
		{
			return "CASSETTE";
		}

		// Data wrappers
		public function get Reactor():uint
		{
			return super.flash_proxy::getProperty("reactor");
		}
		
		public function get Available():Boolean
		{
			return super.flash_proxy::getProperty("available");
		}
		public function set Available(value:Boolean):void
		{
			super.flash_proxy::setProperty("available", value);
		}
		
		public function get Reagents():Array
		{
			// Parse the reagents
			if (m_pReagents == null)
			{
				m_pReagents = new Array();
				var pReagents:Array = super.flash_proxy::getProperty("reagents");
				for each (var pReagentObject:Object in pReagents)
				{
					var pReagent:Reagent = new Reagent(null, pReagentObject);
					m_pReagents.push(pReagent);
				}
			}
			return m_pReagents;
		}

		// Format additional component details
		protected override function FormatComponentDetails():String
		{
			var sCassetteDetails:String = JSONDataObject("reactor", Reactor);
			sCassetteDetails += JSONDataObject("available", Available, false);
			return sCassetteDetails;
		}

		// State components
		private var m_pReagents:Array;
	}
}
