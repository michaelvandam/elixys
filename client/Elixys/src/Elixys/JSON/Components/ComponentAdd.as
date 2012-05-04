package Elixys.JSON.Components
{
	import Elixys.Assets.Constants;
	import Elixys.JSON.JSONObject;
	import Elixys.JSON.State.Reagent;
	
	import flash.utils.flash_proxy;
	
	public class ComponentAdd extends ComponentBase
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
			if ((ComponentType != null) && (ComponentType != COMPONENTTYPE))
			{
				throw new Error("State object mismatch");
			}
		}

		// Static component type and skins
		public static function get COMPONENTTYPE():String
		{
			return "ADD";
		}
		public static function get SKINUP():Class
		{
			return tools_add_up;
		}
		public static function get SKINDOWN():Class
		{
			return tools_add_down;
		}
		public static function get SKINDISABLED():Class
		{
			return tools_add_disabled;
		}
		public static function get SKINACTIVE():Class
		{
			return tools_add_active;
		}

		// Static field details
		public static var FIELDCOUNT:int = 5;
		public static var FIELDLABELS:Array = [
			"REACTOR", 
			"REAGENT", 
			"POSITION", 
			"DURATION", 
			"PRESSURE"
		];
		public static var FIELDTYPES:Array = [
			Constants.TYPE_DROPDOWN, 
			Constants.TYPE_DROPDOWN, 
			Constants.TYPE_DROPDOWN, 
			Constants.TYPE_INPUT, 
			Constants.TYPE_INPUT
		];
		public static var FIELDUNITS:Array = [
			"", 
			"", 
			"", 
			"SECONDS", 
			"PSI"
		];
		public static var FIELDPROPERTIES:Array = [
			"Reactor", 
			"AddReagent", 
			"DeliveryPosition", 
			"DeliveryTime",
			"DeliveryPressure"
		];

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

		// Component comparison function.  Returns true if the components are equal, false otherwise.
		public static function CompareComponents(pComponentA:ComponentBase, pComponentB:ComponentBase):Boolean
		{
			var pComponentAddA:ComponentAdd = new ComponentAdd(null, pComponentA);
			var pComponentAddB:ComponentAdd = new ComponentAdd(null, pComponentB);
			if (pComponentAddA.Reactor != pComponentAddB.Reactor)
			{
				return false;
			}
			if (!Reagent.CompareReagents(pComponentAddA.AddReagent, pComponentAddB.AddReagent))
			{
				return false;
			}
			if (pComponentAddA.AddReagentValidation != pComponentAddB.AddReagentValidation)
			{
				return false;
			}
			if (pComponentAddA.DeliveryPosition != pComponentAddB.DeliveryPosition)
			{
				return false;
			}
			if (pComponentAddA.DeliveryTime != pComponentAddB.DeliveryTime)
			{
				return false;
			}
			if (pComponentAddA.DeliveryPressure != pComponentAddB.DeliveryPressure)
			{
				return false;
			}
			return true;
		}

		// Validates the add component
		public override function Validate():void
		{
			m_sReactorError = ValidateField(Reactor, ReactorValidation);
			m_sAddReagentError = ValidateField(AddReagent, AddReagentValidation);
			m_sDeliveryPositionError = ValidateField(DeliveryPosition, DeliveryPositionValidation);
			m_sDeliveryTimeError = ValidateField(DeliveryTime, DeliveryTimeValidation);
			m_sDeliveryPressureError = ValidateField(DeliveryPressure, DeliveryPressureValidation);
		}
		
		// Validation fields
		public function get ReactorError():String
		{
			return m_sReactorError;
		}
		public function get AddReagentError():String
		{
			return m_sAddReagentError;
		}
		public function get DeliveryPositionError():String
		{
			return m_sDeliveryPositionError;
		}
		public function get DeliveryTimeError():String
		{
			return m_sDeliveryTimeError;
		}
		public function get DeliveryPressureError():String
		{
			return m_sDeliveryPressureError;
		}
		
		// State components
		private var m_pReagent:Reagent;
		
		// Default format
		static public var DEFAULT:String = "{" +
			"\"type\":\"component\"," +
			"\"componenttype\":\"ADD\"," +
			"\"id\":0," +
			"\"note\":\"\"," +
			"\"reactor\":0," +
			"\"reagent\":" + Reagent.DEFAULT + "," +
			"\"deliveryposition\":0," +
			"\"deliverytime\":0," +
			"\"deliverypressure\":0}";

		// Validation errors
		protected var m_sReactorError:String = "";
		protected var m_sAddReagentError:String = "";
		protected var m_sDeliveryPositionError:String = "";
		protected var m_sDeliveryTimeError:String = "";
		protected var m_sDeliveryPressureError:String = "";
	}
}
