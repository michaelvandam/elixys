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
					m_pReagents.push(pReagentObject);
				}
			}
			return m_pReagents;
		}

		// Type
		static public var TYPE:String = "CASSETTE";

		// State components
		private var m_pReagents:Array;
	}
}
