package Elixys.Objects
{
	import flash.utils.flash_proxy;
	
	public class ComponentEluteF18 extends Component
	{
		// Constructor
		public function ComponentEluteF18(data:String = null, existingcontent:Object = null)
		{
			// Call the base constructor
			if ((data == null) && (existingcontent == null))
			{
				data = DEFAULT;
			}
			super(data, existingcontent);
			
			// Validate the object type
			if ((ComponentType != null) && (ComponentType != TYPE))
			{
				throw new Error("State object mismatch");
			}
		}

		// Data wrappers
		public function get EluteTime():uint
		{
			return super.flash_proxy::getProperty("elutetime");
		}
		public function set EluteTime(value:uint):void
		{
			super.flash_proxy::setProperty("elutetime", value);
		}
		
		public function get EluteTimeValidation():String
		{
			return super.flash_proxy::getProperty("elutetimevalidation");
		}
		
		public function get ElutePressure():uint
		{
			return super.flash_proxy::getProperty("elutepressure");
		}
		public function set ElutePressure(value:uint):void
		{
			super.flash_proxy::setProperty("elutepressure", value);
		}
		
		public function get ElutePressureValidation():String
		{
			return super.flash_proxy::getProperty("elutepressurevalidation");
		}

		public function get EluteReagent():Reagent
		{
			if (m_pReagent == null)
			{
				m_pReagent = new Reagent(null, super.flash_proxy::getProperty("reagent"));
			}
			return m_pReagent;
		}
		public function set EluteReagent(value:Reagent):void
		{
			super.flash_proxy::setProperty("reagent", value);
			m_pReagent = null;
		}
		
		public function get EluteReagentValidation():String
		{
			return super.flash_proxy::getProperty("reagentvalidation");
		}
		
		// Format additional component details
		protected override function FormatComponentDetails():String
		{
			var sEluteF18Details:String = JSONDataObject("elutetime", EluteTime);
			sEluteF18Details += JSONDataObject("elutepressure", ElutePressure);
			sEluteF18Details += JSONDataObject("reagent", EluteReagent.ReagentID, false);
			return sEluteF18Details;
		}

		// Type
		static public var TYPE:String = "ELUTEF18";

		// State components
		private var m_pReagent:Reagent;

		// Default format
		static public var DEFAULT:String = "{" +
			"\"type\":\"component\"," +
			"\"componenttype\":\"ELUTEF18\"," +
			"\"id\":0," +
			"\"name\":\"Elute F18\"," +
			"\"elutetime\":0," +
			"\"elutepressure\":0," +
			"\"reagent\":" + Reagent.DEFAULT + "}";
	}
}