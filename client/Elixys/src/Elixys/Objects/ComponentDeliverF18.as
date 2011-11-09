package Elixys.Objects
{
	import flash.utils.flash_proxy;
	
	public class ComponentDeliverF18 extends Component
	{
		// Constructor
		public function ComponentDeliverF18(data:String = null, existingcontent:Object = null)
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
		public function get TrapTime():uint
		{
			return super.flash_proxy::getProperty("traptime");
		}
		public function set TrapTime(value:uint):void
		{
			super.flash_proxy::setProperty("traptime", value);
		}
		
		public function get TrapTimeValidation():String
		{
			return super.flash_proxy::getProperty("traptimevalidation");
		}

		public function get TrapPressure():uint
		{
			return super.flash_proxy::getProperty("trappressure");
		}
		public function set TrapPressure(value:uint):void
		{
			super.flash_proxy::setProperty("trappressure", value);
		}
		
		public function get TrapPressureValidation():String
		{
			return super.flash_proxy::getProperty("trappressurevalidation");
		}
		
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
		
		// Format additional component details
		protected override function FormatComponentDetails():String
		{
			var sDeliverF18Details:String = JSONDataObject("traptime", TrapTime);
			sDeliverF18Details += JSONDataObject("trappressure", TrapPressure);
			sDeliverF18Details += JSONDataObject("elutetime", EluteTime);
			sDeliverF18Details += JSONDataObject("elutepressure", ElutePressure, false);
			return sDeliverF18Details;
		}

		// Type
		static public var TYPE:String = "DELIVERF18";

		// Default format
		static public var DEFAULT:String = "{" +
			"\"type\":\"component\"," +
			"\"componenttype\":\"DELIVERF18\"," +
			"\"id\":0," +
			"\"name\":\"Deliver F18\"," +
			"\"traptime\":0," +
			"\"trappressure\":0," +
			"\"elutetime\":0," +
			"\"elutepressure\":0}";
	}
}
