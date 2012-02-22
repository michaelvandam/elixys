package Elixys.Objects
{
	import flash.utils.flash_proxy;
	
	public class ComponentAdd extends Component
	{
		// Constructor
		public function ComponentAdd(data:String = null, existingcontent:Object = null)
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
		public function get Reactor():uint
		{
			return super.flash_proxy::getProperty("reactor");
		}
		public function set Reactor(value:uint):void
		{
			super.flash_proxy::setProperty("reactor", value);
		}
				
		public function get ReactorValidation():String
		{
			return super.flash_proxy::getProperty("reactorvalidation");
		}

		public function get AddReagent():Reagent
		{
			if (m_pReagent == null)
			{
				m_pReagent = new Reagent(null, super.flash_proxy::getProperty("reagent"));
			}
			return m_pReagent;
		}
		public function set AddReagent(value:Reagent):void
		{
			super.flash_proxy::setProperty("reagent", value);
			m_pReagent = null;
		}
		
		public function get AddReagentValidation():String
		{
			return super.flash_proxy::getProperty("reagentvalidation");
		}

		public function get DeliveryPosition():uint
		{
			return super.flash_proxy::getProperty("deliveryposition");
		}
		public function set DeliveryPosition(value:uint):void
		{
			super.flash_proxy::setProperty("deliveryposition", value);
		}
		
		public function get DeliveryPositionValidation():String
		{
			return super.flash_proxy::getProperty("deliverypositionvalidation");
		}

		public function get DeliveryTime():uint
		{
			return super.flash_proxy::getProperty("deliverytime");
		}
		public function set DeliveryTime(value:uint):void
		{
			super.flash_proxy::setProperty("deliverytime", value);
		}
		
		public function get DeliveryTimeValidation():String
		{
			return super.flash_proxy::getProperty("deliverytimevalidation");
		}
		
		public function get DeliveryPressure():Number
		{
			return super.flash_proxy::getProperty("deliverypressure");
		}
		public function set DeliveryPressure(value:Number):void
		{
			super.flash_proxy::setProperty("deliverypressure", value);
		}
		
		public function get DeliveryPressureValidation():String
		{
			return super.flash_proxy::getProperty("deliverypressurevalidation");
		}
		
		// Format additional component details
		protected override function FormatComponentDetails():String
		{
			var sAddDetails:String = JSONDataObject("reactor", Reactor);
			sAddDetails += JSONDataObject("reagent", AddReagent.ReagentID);
			sAddDetails += JSONDataObject("deliveryposition", DeliveryPosition);
			sAddDetails += JSONDataObject("deliverytime", DeliveryTime);
			sAddDetails += JSONDataObject("deliverypressure", DeliveryPressure, false);
			return sAddDetails;
		}

		// Type
		static public var TYPE:String = "ADD";
		
		// State components
		private var m_pReagent:Reagent;
		
		// Default format
		static public var DEFAULT:String = "{" +
			"\"type\":\"component\"," +
			"\"componenttype\":\"ADD\"," +
			"\"id\":0," +
			"\"name\":\"Add\"," +
			"\"reactor\":0," +
			"\"reagent\":" + Reagent.DEFAULT + "," +
			"\"deliveryposition\":0," +
			"\"deliverytime\":0," +
			"\"deliverypressure\":0}";
	}
}
