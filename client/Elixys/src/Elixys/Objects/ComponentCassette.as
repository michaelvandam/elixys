package Elixys.Objects
{
	import flash.utils.flash_proxy;
	
	public class ComponentCassette extends Component
	{
		// Constructor
		public function ComponentCassette(data:String = null, existingcontent:Object = null)
		{
			// Call the base constructor
			super(data, existingcontent);
			
			// Validate the object type
			if ((ComponentType != null) && (ComponentType != TYPE))
			{
				throw new Error("State object mismatch");
			}
		}

		// Data wrappers
		public function get Reactor():uint
		{
			return super.flash_proxy::getProperty("reactor");
		}
		
		public function get ReactorDescription():String
		{
			return super.flash_proxy::getProperty("reactordescription");
		}
		
		public function get ReactorValidation():String
		{
			return super.flash_proxy::getProperty("reactorvalidation");
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

		// Type
		static public var TYPE:String = "CASSETTE";

		// State components
		private var m_pReagents:Array;
	}
}
